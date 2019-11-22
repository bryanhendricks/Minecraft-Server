#!/usr/bin/env python3
import boto3
from subprocess import call
import time
from mcstatus import MinecraftServer
import configparser


print("Content-Type: text/html\n")

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

# Get the server status
full_status = ec2.describe_instances(
    InstanceIds=['i-074c82fc5718bf939']
)
server_state = full_status['Reservations'][0]['Instances'][0]['State']['Name']
# Check if the server is stopped
if server_state == 'stopped':
    # Start the server
    try:
        ec2.start_instances(
            InstanceIds=['i-074c82fc5718bf939']
        )
    except:
        print('Something went wrong while starting the server, tell Bryan to fix it')
        exit(0)
    # Print a status message
    print('AWS server starting...', end='', flush=True)

    # Wait for the AWS server to start
    while True:
        time.sleep(3)
        # Get the server status
        full_status = ec2.describe_instances(
            InstanceIds=['i-074c82fc5718bf939']
        )
        server_state = full_status['Reservations'][0]['Instances'][0]['State']['Name']
        if server_state != 'running':
            print('.', end='', flush=True)
        else:
            print(' Done</br>')
            break
else:
    # The AWS server is up - send the browser back to the home page
    print('<meta http-equiv="refresh" content="0;url=/" />')
    exit(0)

# Print a status message
print('MineCraft instance starting...', end='', flush=True)

# Wait for the MineCraft instance to start
while True:
    time.sleep(3)
    # Get the MineCraft instance status
    try:
        server = MinecraftServer('52.52.246.252', 25565)
        mc_status = server.status()
        print(' Done - the MineCraft instance is up, with a latency of {} ms'.format(mc_status.latency))
        break
    except:
        print('.', end='', flush=True)
