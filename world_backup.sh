#/bin/bash

# Fill in the following for your 'MinecraftServer' EC2 instance (not the 'LazyMcProxy' instance)
# See https://console.aws.amazon.com/ec2/home#Instances to get this information
REMOTE_HOST="<MINECRAFT SERVER 'PUBLIC IPv4 DNS' - looks like 'ec2-##-##-###-###.<REGION>.compute.amazonaws.com')>"
PATH_TO_SSH_KEY="<PATH TO SSH KEY FILE - should be the '.pem' file you downloaded. You may need to run 'chmod 0400 <path to .pem file>' first"

# <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>

REMOTE_USER="ubuntu"        # Remote SSH username
REMOTE_SERVICE_NAME="minecraft" # Name of the service to stop/start
REMOTE_FOLDER_PATH="/minecraft/better-mc-server/world" # Folder to zip on the remote server
ZIP_FILE_NAME="world_backup_$(date +%Y%m%d_%H%M%S).zip" # Zip file name with timestamp
LOCAL_DOWNLOAD_PATH="./"           # Local folder to download the zip file

# Stop the remote service
echo "Stopping the Minecraft server: $REMOTE_SERVICE_NAME..."
ssh -i $PATH_TO_SSH_KEY "$REMOTE_USER@$REMOTE_HOST" "sudo systemctl stop $REMOTE_SERVICE_NAME"
if [ $? -ne 0 ]; then
    echo "Failed to stop the service. Exiting."
    exit 1
fi

# Zip the remote folder
echo "Zipping up the world data folder: $REMOTE_FOLDER_PATH..."
ssh -i $PATH_TO_SSH_KEY "$REMOTE_USER@$REMOTE_HOST" "zip -r /tmp/$ZIP_FILE_NAME $REMOTE_FOLDER_PATH"
if [ $? -ne 0 ]; then
    echo "Failed to zip the folder. Exiting."
    exit 1
fi

# Download the zipped folder
echo "Downloading the zipped world data to: $LOCAL_DOWNLOAD_PATH..."
scp -i $PATH_TO_SSH_KEY "$REMOTE_USER@$REMOTE_HOST:/tmp/$ZIP_FILE_NAME" "$LOCAL_DOWNLOAD_PATH"
if [ $? -ne 0 ]; then
    echo "Failed to download the zip file. Exiting."
    exit 1
fi

# Start the remote service
echo "Restarting the Minecraft server: $REMOTE_SERVICE_NAME..."
ssh -i $PATH_TO_SSH_KEY "$REMOTE_USER@$REMOTE_HOST" "sudo systemctl start $REMOTE_SERVICE_NAME"
if [ $? -ne 0 ]; then
    echo "Failed to start the service. Please check the remote server."
    exit 1
fi

# Clean up the remote zip file
echo "Deleting the remote zip file..."
ssh -i $PATH_TO_SSH_KEY "$REMOTE_USER@$REMOTE_HOST" "rm /tmp/$ZIP_FILE_NAME"
if [ $? -ne 0 ]; then
    echo "Failed to clean up the remote zip file. Please check the remote server."
fi

echo "Successfully downloaded world data"
