#!/bin/bash

set -e

# Create ECS Services script
# This script creates all 7 ECS services in the UNIVERSITY_SERVICES_HUB cluster
# It automatically handles VPC, Security Group, and Subnet setup

CLUSTER_NAME="UNIVERSITY_SERVICES_HUB"
REGION="us-east-2"
ACCOUNT_ID="643771447281"

echo "================================================"
echo "ECS Services Setup Script"
echo "================================================"
echo "Cluster: $CLUSTER_NAME"
echo "Region: $REGION"
echo ""

# Get default VPC and subnet
echo "Step 1: Getting VPC and Subnet information..."
VPC_ID=$(aws ec2 describe-vpcs --region $REGION --filters "Name=isDefault,Values=true" --query 'Vpcs[0].VpcId' --output text)
SUBNET_ID=$(aws ec2 describe-subnets --region $REGION --filters "Name=vpc-id,Values=$VPC_ID" --query 'Subnets[0].SubnetId' --output text)

echo "✅ VPC ID: $VPC_ID"
echo "✅ Subnet ID: $SUBNET_ID"
echo ""

# Create or get security group
echo "Step 2: Creating Security Group..."
SG_NAME="ecs-campus-services-sg"
SG_ID=$(aws ec2 describe-security-groups \
    --region $REGION \
    --filters "Name=group-name,Values=$SG_NAME" "Name=vpc-id,Values=$VPC_ID" \
    --query 'SecurityGroups[0].GroupId' \
    --output text 2>/dev/null || echo "NONE")

if [ "$SG_ID" == "NONE" ]; then
    echo "Creating new security group: $SG_NAME"
    SG_ID=$(aws ec2 create-security-group \
        --group-name "$SG_NAME" \
        --description "Security group for ECS Campus Services" \
        --vpc-id "$VPC_ID" \
        --region $REGION \
        --query 'GroupId' \
        --output text)
    
    # Allow all inbound traffic (for testing - restrict in production)
    aws ec2 authorize-security-group-ingress \
        --group-id "$SG_ID" \
        --protocol all \
        --cidr 0.0.0.0/0 \
        --region $REGION 2>/dev/null || true
    
    echo "✅ Security Group created: $SG_ID"
else
    echo "✅ Using existing Security Group: $SG_ID"
fi
echo ""

# Step 3: Create CloudWatch Log Group
echo "Step 3: Creating CloudWatch Log Group..."
aws logs create-log-group \
    --log-group-name /ecs/campus-services \
    --region $REGION 2>/dev/null || echo "Log group already exists"
echo "✅ CloudWatch log group ready: /ecs/campus-services"
echo ""

# Step 4: Register Task Definitions
echo "Step 4: Registering Task Definitions..."
for task_file in ecs/task-definition-*.json; do
    echo "Registering: $task_file"
    aws ecs register-task-definition \
        --cli-input-json file://$task_file \
        --region $REGION 2>&1 || echo "Warning: Failed to register $task_file"
done
echo "✅ Task definitions registered"
echo ""

# Define services array: [service_name, task_definition_name, container_port]
declare -a SERVICES=(
    "postgres-service:campus-services-postgres:5432"
    "booking-service:campus-services-booking:8000"
    "gateway-service:campus-services-gateway:5001"
    "user-management-service:campus-services-user-management:8002"
    "gpa-calculator-service:campus-services-gpa-calculator:8003"
    "notification-service:campus-services-notification:8004"
    "maintenance-service:campus-services-maintenance:8080"
)

echo "Step 5: Creating ECS Services..."
echo "---"

for service_pair in "${SERVICES[@]}"; do
    IFS=':' read -r service_name task_def container_port <<< "$service_pair"
    
    echo "Creating: $service_name"
    
    aws ecs create-service \
        --cluster "$CLUSTER_NAME" \
        --service-name "$service_name" \
        --task-definition "$task_def" \
        --desired-count 1 \
        --region "$REGION" \
        --launch-type FARGATE \
        --network-configuration "awsvpcConfiguration={subnets=[$SUBNET_ID],securityGroups=[$SG_ID],assignPublicIp=ENABLED}" \
        2>&1 || echo "Note: Service may already exist or encountered an error"
    
    echo "✅ $service_name creation initiated"
    echo "---"
done

echo ""
echo "================================================"
echo "✅ Service Setup Complete!"
echo "================================================"
echo ""
echo "Verify services:"
echo "  aws ecs list-services --cluster $CLUSTER_NAME --region $REGION"
echo ""
echo "Check service status:"
echo "  aws ecs describe-services --cluster $CLUSTER_NAME --region $REGION --services postgres-service booking-service gateway-service user-management-service gpa-calculator-service notification-service maintenance-service"
echo ""
echo "View CloudWatch logs:"
echo "  aws logs tail /ecs/campus-services --follow --region $REGION"
echo ""
echo "Auto-generated resources:"
echo "  VPC: $VPC_ID"
echo "  Subnet: $SUBNET_ID"
echo "  Security Group: $SG_ID"
