#!/bin/bash
JAR_PATH='/home/ubuntu/minecraft-server/minecraft_server.1.18.1.jar'
tmux new-session -d -s MinecraftServer 'cd /home/ubuntu/minecraft-server/; sudo java -Xms2G -Xmx14G -jar $JAR_PATH nogui; exec bash'
