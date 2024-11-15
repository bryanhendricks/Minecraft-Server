import time
from mcstatus import JavaServer

print('Waiting for server to go live...')
while True:
    try:
        server = JavaServer('13.57.131.204', 25565)
        mc_status = server.status()
        # Server is up, exit loop
        break
    except:
        # Server is down, do nothing
        pass
    time.sleep(10)

print('<><><><><><><><><><><><><><><><><><>')
print('           Server is up')
print('<><><><><><><><><><><><><><><><><><>')
