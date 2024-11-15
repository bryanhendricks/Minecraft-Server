#!/bin/bash

# Install dependencies
sudo apt update -y
sudo apt install -y python3 python3-pip awscli jq ntp
pip3 install mcstatus

# Start NTP
sudo systemctl start ntp
sudo systemctl enable ntp

# Download lazymc and startup/shutdown scripts
cd /home/ubuntu
wget https://raw.githubusercontent.com/bryanhendricks/minecraft-server/refs/heads/master/lazymc
wget https://raw.githubusercontent.com/bryanhendricks/minecraft-server/refs/heads/master/lazymc_scripts/startup.sh
wget https://raw.githubusercontent.com/bryanhendricks/minecraft-server/refs/heads/master/lazymc_scripts/shutdown.sh
chmod +x lazymc startup.sh shutdown.sh

# Create lazymc config file
cat > /home/ubuntu/config.toml <<EOL
[public]
address = "0.0.0.0:25565"
version = "1.20.1"

[server]
address = "__MINECRAFT_SERVER_IP__:25565"
command = "/home/ubuntu/startup.sh __MINECRAFT_INSTANCE_ID__ __SERVER_REGION__"
stop_command = "/home/ubuntu/shutdown.sh __MINECRAFT_INSTANCE_ID__ __SERVER_REGION__"
forge = true
start_timeout = 900
stop_timeout = 500

[motd]
from_server = true

[time]
sleep_after = 300
minimum_online_time = 120

[join]
methods = ["hold", "kick", "forward"]

[join.forward]
address = "__MINECRAFT_SERVER_IP__:25565"
EOL
sudo chown ubuntu:ubuntu /home/ubuntu/lazymc /home/ubuntu/config.toml

# Create lazymc.service file
sudo tee /etc/systemd/system/lazymc.service > /dev/null <<EOL
[Unit]
Description=LazyMC Proxy Service
After=network.target

[Service]
Type=simple
User=ubuntu
Environment="PATH=/usr/local/bin:/usr/bin:/bin"
ExecStart=/home/ubuntu/lazymc -c /home/ubuntu/config.toml
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOL

# Reload systemd and start lazymc service
sudo systemctl daemon-reload
sudo systemctl enable lazymc
sudo systemctl start lazymc
