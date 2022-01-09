import os, sys
from flask import Flask, request, redirect
import time
sys.path.append(os.path.dirname(__file__))
from src import connect_aws, get_server_status, start_server
from mcstatus import MinecraftServer


MINECRAFT_SERVER_INSTANCE_ID = 'i-00c2d1af54569b884'
WEBSERVER_PUBLIC_IP_ADDRESS = '54.241.254.8'
MINECRAFT_SERVER_IP = '13.52.129.204'
MINECRAFT_SERVER_PORT = 25565


app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def home_page():
    # Handle page load
    if request.method == 'GET':
        print('Home page load')
        page_data = """
            <form method="post" action="/">
                <input type="submit" value="Start server" name="start_server"/>
            </form>
        """
        return page_data
    # Handle button press
    elif request.method == 'POST':
        if request.form.get('start_server') == 'Start server':
            print('"Start server" button pressed')
            # Try to start the server
            server_status = start_server(connect_aws(), MINECRAFT_SERVER_INSTANCE_ID)
            if not server_status:
                # An error occurred starting the server - display an error message
                return '<h1>Something went wrong while starting the server, tell Bryan to fix it</h1>'
            # Redirect to server status page
            return redirect('http://%s/status' % WEBSERVER_PUBLIC_IP_ADDRESS)


@app.route('/status')
def status_page():
    print('Getting server status')
    # Get and display the server status
    server_status = get_server_status(connect_aws(), MINECRAFT_SERVER_INSTANCE_ID)
    if server_status == 'running':
        try:
            server = MinecraftServer(MINECRAFT_SERVER_IP, MINECRAFT_SERVER_PORT)
            mc_status = server.status()
            player_count = mc_status.players.online
            # Server is up
            server_status = 'running<br>Player count: ' + str(player_count)
        except:
            # Server is down
            server_status = 'starting'
    return '<h1>Server status: %s</h1>' % server_status


app.run(host='0.0.0.0', port=80)
