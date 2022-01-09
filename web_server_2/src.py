import boto3
import configparser


def connect_aws():
    # Get credentials
    print('Getting AWS credentials')
    creds_config = configparser.ConfigParser()
    creds_config.read('/home/ubuntu/minecraft-server/web_server_2/credentials')
    ACCESS_KEY = creds_config['default']['aws_access_key_id']
    SECRET_KEY = creds_config['default']['aws_secret_access_key']
    # Connect to AWS
    print('Connecting to AWS')
    ec2 = boto3.client(
        'ec2',
        region_name='us-west-1',
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY
    )
    print('Done connecting to AWS')
    return ec2


def get_server_status(ec2, MINECRAFT_SERVER_INSTANCE_ID):
    # Get the server status
    print('Getting server status')
    full_status = ec2.describe_instances(
        InstanceIds=[MINECRAFT_SERVER_INSTANCE_ID]
    )
    server_status = full_status['Reservations'][0]['Instances'][0]['State']['Name']
    print('Server status: ' + str(server_status))
    return server_status


def start_server(ec2, MINECRAFT_SERVER_INSTANCE_ID):
    # Check if the server is stopped
    server_status = get_server_status(ec2, MINECRAFT_SERVER_INSTANCE_ID)
    if server_status == 'stopped':
        # Start the server
        print('Server is stopped, attempting to start')
        try:
            ec2.start_instances(
                InstanceIds=[MINECRAFT_SERVER_INSTANCE_ID]
            )
        except Exception as e:
            print('Error starting server: ' + str(e))
            return False
        return True
    else:
        # The AWS server is starting up, or already up - return the status
        print('Server is not stopped (status: %s), returning server status' % server_status)
        return server_status