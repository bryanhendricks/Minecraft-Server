#!/usr/bin/env python3
from mcstatus import JavaServer
import boto3
import configparser

MINECRAFT_SERVER_INSTANCE_ID = 'i-00c2d1af54569b884'
MINECRAFT_SERVER_IP_ADDRESS = '52.53.212.107'

# Print the header
print('Content-Type: text/html\n')

# Gather the unformatted HTML for the opening page
with open('raw_form.html', 'r') as html_file:
        raw_html_form = html_file.read()

# Get credentials
creds_config = configparser.ConfigParser()
creds_config.read('/home/ubuntu/minecraft-server/web_server/credentials')
ACCESS_KEY = creds_config['default']['aws_access_key_id']
SECRET_KEY = creds_config['default']['aws_secret_access_key']

# Get the AWS server status
try:
    ec2 = boto3.client(
        'ec2',
        region_name='us-west-1',
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY
    )
except Exception as e:
    print('Exception: ' + str(e))
full_status = ec2.describe_instances(
    InstanceIds=[MINECRAFT_SERVER_INSTANCE_ID]
)
server_state = full_status['Reservations'][0]['Instances'][0]['State']['Name']


if server_state == 'stopped':
    raw_html_form = raw_html_form.format("""
    The server has not been started - <input type = "submit" value = "click here to start the server" />
    """)
elif server_state == 'pending':
    raw_html_form = raw_html_form.format("""
    The server is still starting, give it a minute or two
    """)
elif server_state == 'running':
    # Get the MC server status
    try:
        server = JavaServer(MINECRAFT_SERVER_IP_ADDRESS, 25565)
        mc_status = server.status()
        raw_html_form = raw_html_form.format("""
        The server is up - it has {0} players online, and a latency of {1} ms""".format(mc_status.players.online, mc_status.latency)
        )
    except:
        raw_html_form = raw_html_form.format("""
        The server has been started, but the MineCraft instance has not gone live yet - if this persists for more than a few minutes, tell Bryan to go fix it
        """)
else:
    raw_html_form = raw_html_form.format("""
    The server is currently shutting down, come back in a minute or two
    """)

print(raw_html_form)
