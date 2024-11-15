#!/bin/bash
INSTANCE_ID="$1"   # First argument is the instance ID
AWS_REGION="$2"    # Second argument is the AWS region

# Function to get the current state of the instance
get_instance_state() {
    aws ec2 describe-instances \
        --instance-ids "$INSTANCE_ID" \
        --region "$AWS_REGION" \
        --query 'Reservations[0].Instances[0].State.Name' \
        --output text
}

# Function to wait for the instance to reach a desired state
wait_for_state() {
    local desired_state="$1"
    echo "Waiting for instance to be in '$desired_state' state..."
    aws ec2 wait "instance-$desired_state" --instance-ids "$INSTANCE_ID" --region "$AWS_REGION"
    echo "Instance is now in '$desired_state' state."
}

# Get the current state of the instance
INSTANCE_STATE=$(get_instance_state)
echo "Current instance state: $INSTANCE_STATE"

case "$INSTANCE_STATE" in
    pending)
        echo "Instance is starting up. Proceeding..."
        ;;
    running)
        echo "Instance is already running. Proceeding..."
        ;;
    stopping|shutting-down)
        echo "Instance is stopping. Waiting for it to stop..."
        wait_for_state "stopped"
        echo "Starting the instance..."
        aws ec2 start-instances --instance-ids "$INSTANCE_ID" --region "$AWS_REGION"
        ;;
    stopped)
        echo "Instance is stopped. Starting it..."
        aws ec2 start-instances --instance-ids "$INSTANCE_ID" --region "$AWS_REGION"
        ;;
    terminated)
        echo "Instance is terminated and cannot be started. Exiting."
        exit 1
        ;;
    *)
        echo "Unknown instance state: $INSTANCE_STATE. Exiting."
        exit 1
        ;;
esac

# If the instance was started, wait until it's running
if [[ "$INSTANCE_STATE" != "running" && "$INSTANCE_STATE" != "pending" ]]; then
    wait_for_state "running"
fi

# Get the private IP address of the EC2 instance
SERVER_IP=$(aws ec2 describe-instances \
    --instance-ids "$INSTANCE_ID" \
    --region "$AWS_REGION" \
    --query 'Reservations[0].Instances[0].PrivateIpAddress' \
    --output text)

echo "Server IP is $SERVER_IP"

# Wait until the Minecraft server port (default 25565) is open
echo "Waiting for Minecraft server to be ready..."
while ! mcstatus ${SERVER_IP}:25565 ping >/dev/null 2>&1; do
    sleep 5
done
echo "Minecraft server is ready."
