# Install dependencies
sudo apt update -y
sudo apt install -y wget unzip ntp nfs-common openjdk-17-jdk

# Start NTP via Chrony
sudo systemctl start ntp
sudo systemctl enable ntp

# Start the AWS SSM Agent
sudo snap start amazon-ssm-agent
sudo systemctl enable snap.amazon-ssm-agent.amazon-ssm-agent.service

# Create minecraft directory
sudo mkdir -p /minecraft

# Add EFS mount to /etc/fstab
echo "__EFS_FILE_SYSTEM_ID__.efs.__AWS_REGION__.amazonaws.com:/ /minecraft nfs4 defaults,_netdev 0 0" | sudo tee -a /etc/fstab

# Mount the EFS file system
sudo mount -a

# Wait for EFS drive to be mounted
while ! mountpoint -q /minecraft; do
    echo "Waiting for /minecraft to be mounted..."
    sleep 1
done

# Variables
MODPACK_URL="https://mediafilez.forgecdn.net/files/5854/178/BMC4_FORGE_Server_Pack_v34_HF.zip"
MODPACK_ZIP="BMC4_FORGE_Server_Pack_v34_HF.zip"
MODPACK_DIR="/minecraft/better-mc-server"

# Download the modpack server files if not already downloaded
if [ ! -d "$MODPACK_DIR" ]; then
    echo "Downloading modpack server files..."
    wget $MODPACK_URL -O "/minecraft/$MODPACK_ZIP"
    echo "Unzipping modpack..."
    unzip "/minecraft/$MODPACK_ZIP" -d "$MODPACK_DIR"
    rm /minecraft/$MODPACK_ZIP
    echo "eula=true" > "$MODPACK_DIR/eula.txt"
    # Make the start script executable
    chmod +x "$MODPACK_DIR/start.sh"
fi

# Set the minecraft folder to be owned by the ubuntu user
sudo chown -R ubuntu:ubuntu /minecraft

# Disable the broken NoChatReports mod
mv /minecraft/better-mc-server/mods/NoChatReports-FORGE-1.20.1-v2.2.2.jar /minecraft/better-mc-server/mods/NoChatReports-FORGE-1.20.1-v2.2.2.jar.DISABLE

# Create Minecraft service unit file
sudo cat > /etc/systemd/system/minecraft.service <<EOL
[Unit]
Description=Minecraft Server
After=network.target minecraft.mount
Requires=minecraft.mount

[Service]
Type=simple
User=ubuntu
WorkingDirectory=$MODPACK_DIR
ExecStart=/bin/bash ./start.sh
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOL

# Reload systemd and enable the service
sudo systemctl daemon-reload
sudo systemctl enable minecraft.service
sudo systemctl start minecraft.service
