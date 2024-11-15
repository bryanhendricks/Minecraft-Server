#!/bin/bash
INSTANCE_ID="$1"   # First argument is the instance ID
AWS_REGION="$2"    # Second argument is the AWS region

echo "Shutting down server..."
COMMAND_ID=$(aws ssm send-command \
    --document-name "AWS-RunShellScript" \
    --targets "Key=instanceids,Values=$INSTANCE_ID" \
    --parameters 'commands=["sudo systemctl stop minecraft.service"]' \
    --region "$AWS_REGION" \
    --query "Command.CommandId" \
    --output text)

SECONDS=0
while [ $SECONDS -lt 60 ]; do
    STATUS=$(aws ssm list-command-invocations \
        --command-id "$COMMAND_ID" \
        --details \
        --query "CommandInvocations[0].Status" \
        --output text \
        --region "$AWS_REGION")

    if [[ "$STATUS" == "Success" ]]; then
        echo "minecraft.service stopped successfully - shutting down server."
        break
    elif [[ "$STATUS" == "Failed" || "$STATUS" == "Cancelled" ]]; then
        echo "Failed to stop minecraft.service. Shutting down anyways."
        break
    fi

    # Wait a few seconds before checking again
    sleep 5
done

echo "Stopping EC2 instance..."
aws ec2 stop-instances --instance-ids "$INSTANCE_ID" --region "$AWS_REGION"
