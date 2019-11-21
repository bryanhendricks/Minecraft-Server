from mcstatus import MinecraftServer
import time
from subprocess import call
import os


# Wait for the server to start
print('Waiting for server to go live')
while True:
    time.sleep(5)
    try:
        server = MinecraftServer('localhost', 25565)
        mc_status = server.status()
        break
    except:
        print('Server is down - current time: ' + str(int(time.time())))

print('Server is live, checking player counts')
player_last_seen = int(time.time())

while True:
    time.sleep(5)

    # Get the server player count
    try:
        server = MinecraftServer('localhost', 25565)
        mc_status = server.status()
        player_count = mc_status.players.online
    except:
        print('Server is down - current time: ' + str(int(time.time())))
        player_count = 0

    print('Player count: ' + str(player_count))
    # Check if nobody has been online for an extended period of time
    if player_count != 0:
        player_last_seen = int(time.time())
    else:
        print('Player last seen ' + str(int(time.time()) - player_last_seen) + 's ago')
        if int(time.time()) - player_last_seen > 60 * 5:  # 5 minutes
            # Exit the loop to stop the server
            break

print('Shutting down the server')
# Shut down the server
try:
    call(['/home/ec2-user/minecraft_forge_server/stop_mc_server.sh'])
except:
    print('Unable to stop MineCraft instance')

time.sleep(30)

os.system('sudo shutdown now')
