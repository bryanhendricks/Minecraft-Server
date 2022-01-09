import os, sys
from flask import Flask, request, redirect
import time
sys.path.append(os.path.dirname(__file__))
from src import connect_aws, get_server_status


MINECRAFT_SERVER_INSTANCE_ID = 'i-00c2d1af54569b884'
PUBLIC_IP_ADDRESS = '54.241.254.8'

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def home_page():
    # Handle page load
    if request.method == 'GET':
        print('Home page load')
        page_data = """
            <input type="submit" name="submit_button" value="Start server">
        """
        return page_data
    # Handle button press
    elif request.method == 'POST':
        if request.form['submit_button'] == 'Start server':
            print('"Start server" button pressed')
            # Try to start the server
            server_status = get_server_status(connect_aws(), MINECRAFT_SERVER_INSTANCE_ID)
            if not server_status:
                # An error occurred starting the server - display an error message
                return '<h1>Something went wrong while starting the server, tell Bryan to fix it</h1>'
            # Redirect to server status page
            return redirect('http://%s/status' % PUBLIC_IP_ADDRESS)


@app.route('/status')
def status_page():
    print('Getting server status')
    # Get and display the server status
    server_status = get_server_status(connect_aws(), MINECRAFT_SERVER_INSTANCE_ID)
    return '<h1>Server status: %s</h1>' % server_status


app.run(host='0.0.0.0', port=80)
