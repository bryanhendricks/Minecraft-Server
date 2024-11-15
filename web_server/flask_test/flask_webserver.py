from flask import Flask, render_template, redirect, url_for
from mcstatus import JavaServer
import boto3

app = Flask(__name__)


MC_SERVER_AWS_ID = 'i-074c82fc5718bf939'


def get_server_status():
    # Get the AWS server status
    try:
        ec2 = boto3.client(
            'ec2',
            region_name='us-west-1'
        )
        full_status = ec2.describe_instances(
            InstanceIds=[MC_SERVER_AWS_ID]
        )
        server_state = full_status['Reservations'][0]['Instances'][0]['State']['Name']
        return server_state
    except Exception as e:
        print('Error getting server status - error: ' + str(e))
        return None


@app.route('/')
def index():
    # Get the MC server status
    server_state = get_server_status()
    if server_state is None:
        return 'Something broke, go yell at Bryan'

    if server_state == 'stopped':
        # Send a start button
        return render_template('start.html')


@app.route('/start', methods=['POST'])
def start_mc_server():
    return 'Starting MC server'


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
