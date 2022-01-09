#!/bin/bash
tmux new-session -d -s MinecraftServer 'cd /home/ubuntu/minecraft-server/minecraft; java -Xms2G -Xmx14G -jar /home/ubuntu/minecraft-server/paper-1.18.1-140.jar nogui; exec bash'
