#!/usr/bin/env python3
from mcstatus import MinecraftServer
import boto3

# Print the header
print('Content-Type: text/html\n')

# Gather the unformatted HTML for the opening page
with open('start.html', 'r') as html_file:
        raw_html_form = html_file.read()

# Get the AWS server status
try:
    ec2 = boto3.client(
        'ec2',
        region_name = 'us-west-1'
    )
except Exception as e:
    print('Exception: ' + str(e))
full_status = ec2.describe_instances(
    InstanceIds=['i-074c82fc5718bf939']
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
        server = MinecraftServer('52.52.246.252', 25565)
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
