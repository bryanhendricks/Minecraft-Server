import boto3
import configparser


def connect_aws():
    # Get credentials
    creds_config = configparser.ConfigParser()
    creds_config.read('/home/ubuntu/minecraft-server/web_server/credentials')
    ACCESS_KEY = creds_config['default']['aws_access_key_id']
    SECRET_KEY = creds_config['default']['aws_secret_access_key']
    # Get the server status
    ec2 = boto3.client(
        'ec2',
        region_name='us-west-1',
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY
    )
    return ec2


def get_server_status(ec2, MINECRAFT_SERVER_INSTANCE_ID):
    # Get the server status
    full_status = ec2.describe_instances(
        InstanceIds=[MINECRAFT_SERVER_INSTANCE_ID]
    )
    return full_status['Reservations'][0]['Instances'][0]['State']['Name']


def start_server(ec2, MINECRAFT_SERVER_INSTANCE_ID):
    # Check if the server is stopped
    server_status = get_server_status(ec2, MINECRAFT_SERVER_INSTANCE_ID)
    if server_status == 'stopped':
        # Start the server
        try:
            ec2.start_instances(
                InstanceIds=[MINECRAFT_SERVER_INSTANCE_ID]
            )
        except:
            return False, 'Something went wrong while starting the server, tell Bryan to fix it'
    else:
        # The AWS server is starting up, or already up - return the status
        return server_status, ''
