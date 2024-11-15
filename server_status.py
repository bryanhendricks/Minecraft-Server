from mcstatus import JavaServer

server = JavaServer('52.53.212.107', 25565)
status = server.status()
print("The server has {0} players and replied in {1} ms".format(status.players.online, status.latency))
