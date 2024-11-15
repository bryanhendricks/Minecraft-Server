from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_efs as efs,
    RemovalPolicy,
    CfnOutput,
)
from constructs import Construct


class MinecraftServerStack(Stack):
    def __init__(self, scope: Construct, id: str, conf: dict, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # VPC setup

        vpc = ec2.Vpc(
            self,
            "MinecraftVpc",
            max_azs=1,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="MinecraftPublicSubnet",
                    subnet_type=ec2.SubnetType.PUBLIC,
                )
            ],
        )

        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Security group setup

        # Define the security group for the LazyMC proxy
        proxy_sg = ec2.SecurityGroup(
            self,
            "ProxySecurityGroup",
            vpc=vpc,
            description="Security group for LazyMC proxy",
            allow_all_outbound=True,
        )

        # Proxy Security Group: Allow inbound TCP traffic on port 25565 from anywhere
        proxy_sg.add_ingress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(25565),
            description="Allow Minecraft connections on TCP port 25565",
        )

        # Proxy Security Group: Allow SSH access from anywhere
        proxy_sg.add_ingress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(22),
            description="Allow SSH connections",
        )

        # Define the security group for the Minecraft server
        minecraft_sg = ec2.SecurityGroup(
            self,
            "MinecraftSecurityGroup",
            vpc=vpc,
            description="Security group for Minecraft server",
            allow_all_outbound=True,
        )

        # Minecraft Security Group: Allow inbound TCP traffic on port 25565 from the proxy security group
        minecraft_sg.add_ingress_rule(
            peer=proxy_sg,
            connection=ec2.Port.tcp(25565),
            description="Allow Minecraft connections from the proxy on TCP port 25565",
        )

        # If mcstatus uses UDP, allow UDP traffic as well (optional)
        minecraft_sg.add_ingress_rule(
            peer=proxy_sg,
            connection=ec2.Port.udp(25565),
            description="Allow mcstatus queries from the proxy on UDP port 25565",
        )

        # Minecraft Security Group: Allow SSH access from the proxy security group
        minecraft_sg.add_ingress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(22),
            description="Allow SSH connections",
        )

        # Create a security group for EFS
        efs_sg = ec2.SecurityGroup(
            self,
            "EFSSecurityGroup",
            vpc=vpc,
            description="Security group for EFS",
            allow_all_outbound=True,
        )

        # EFS Security Group: Allow inbound NFS traffic from the Minecraft server security group
        efs_sg.add_ingress_rule(
            peer=minecraft_sg,
            connection=ec2.Port.tcp(2049),
            description="Allow NFS traffic from Minecraft server",
        )

        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # EFS setup

        efs_filesystem = efs.FileSystem(
            self,
            "MinecraftEFS",
            vpc=vpc,
            security_group=efs_sg,
            removal_policy=RemovalPolicy.DESTROY,
            lifecycle_policy=efs.LifecyclePolicy.AFTER_14_DAYS,
            out_of_infrequent_access_policy=efs.OutOfInfrequentAccessPolicy.AFTER_1_ACCESS,
            throughput_mode=efs.ThroughputMode.ELASTIC
        )

        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Minecraft EC2 server initialization

        ubuntu_ami = ec2.MachineImage.lookup(
            name="ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*",
            owners=["099720109477"],
            filters={"architecture": ["x86_64"]},
        )

        # Configure the EC2 setup script
        with open("ec2_initialization_scripts/server_setup.sh", "r") as file:
            minecraft_user_data_script = file.read()
        minecraft_user_data_script = (
            minecraft_user_data_script
            .replace("__EFS_FILE_SYSTEM_ID__", efs_filesystem.file_system_id)
            .replace("__AWS_REGION__", self.region)
        )
        user_data_minecraft_server = ec2.UserData.for_linux()
        user_data_minecraft_server.add_commands(minecraft_user_data_script)

        # Create the EC2 instance for the Minecraft server
        minecraft_instance = ec2.Instance(
            self,
            "MinecraftServerInstance",
            instance_name="MinecraftServer",
            instance_type=ec2.InstanceType(conf.get("ec2_type")),
            machine_image=ubuntu_ami,
            vpc=vpc,
            security_group=minecraft_sg,
            user_data=user_data_minecraft_server,
            # Use default root volume size or specify a smaller one
            block_devices=[
                ec2.BlockDevice(
                    device_name="/dev/sda1",
                    volume=ec2.BlockDeviceVolume.ebs(
                        volume_size=8,
                        delete_on_termination=True,
                    ),
                )
            ],
            key_name=conf.get("key_name"),
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
        )
        minecraft_instance.role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSSMManagedInstanceCore")
        )

        minecraft_private_ip = minecraft_instance.instance_private_ip

        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # LazyMC proxy setup

        with open("ec2_initialization_scripts/proxy_setup.sh", "r") as file:
            user_data_script = file.read()
        user_data_script = (
            user_data_script.replace(
                "__MINECRAFT_INSTANCE_ID__", minecraft_instance.instance_id
            )
            .replace("__MINECRAFT_SERVER_IP__", minecraft_private_ip)
            .replace("__SERVER_REGION__", conf["region"])
        )
        user_data = ec2.UserData.for_linux()
        user_data.add_commands(user_data_script)
        proxy_instance = ec2.Instance(
            self,
            "LazyMcProxy",
            instance_name="LazyMcProxy",
            instance_type=ec2.InstanceType("t3a.micro"),
            machine_image=ubuntu_ami,
            vpc=vpc,
            security_group=proxy_sg,
            user_data=user_data,
            key_name=conf.get("key_name"),
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
        )
        proxy_instance.role.attach_inline_policy(
            iam.Policy(
                self,
                "StartStopMinecraftServerPolicy",
                statements=[
                    iam.PolicyStatement(
                        actions=[
                            "ec2:DescribeInstances",
                            "ec2:StartInstances",
                            "ec2:StopInstances",
                        ],
                        resources=["*"],
                    )
                ],
            )
        )
        proxy_instance.role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSSMFullAccess")
        )

        # Allow proxy to use SSM
        proxy_instance.role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSSMManagedInstanceCore")
        )

        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Elastic IP setup

        eip = ec2.CfnEIP(self, "ProxyEIP")
        ec2.CfnEIPAssociation(
            self,
            "EIPAssociation",
            eip=eip.ref,
            instance_id=proxy_instance.instance_id,
        )
        CfnOutput(self, "MinecraftServerPublicIP", value=eip.ref)
