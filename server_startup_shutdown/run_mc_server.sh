#!/bin/bash
tmux new-session -d -s MinecraftServer 'cd /home/ec2-user/hardcore_server/; sudo java -Xms1024M -Xmx3800M -jar craftbukkit-1.14.4-R0.1-SNAPSHOT.jar nogui; exec bash'
