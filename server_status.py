from mcstatus import MinecraftServer

server = MinecraftServer('52.52.246.252', 25565)
status = server.status()
print("The server has {0} players and replied in {1} ms".format(status.players.online, status.latency))
