#!/bin/bash

# AWS App Runner Deployment Script for Palabam Backend
# This script builds and pushes the Docker image to ECR, then updates App Runner service

set -e  # Exit on error

# Configuration
AWS_REGION="${AWS_REGION:-us-east-2}"
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_REPOSITORY="palabam-backend"
APP_RUNNER_SERVICE="palabam-backend"

echo "🚀 Deploying Palabam Backend to AWS App Runner"
echo "Account ID: $AWS_ACCOUNT_ID"
echo "Region: $AWS_REGION"
echo ""

# Step 1: Create ECR repository if it doesn't exist
echo "📦 Checking ECR repository..."
if ! aws ecr describe-repositories --repository-names $ECR_REPOSITORY --region $AWS_REGION &>/dev/null; then
  echo "   Creating ECR repository: $ECR_REPOSITORY"
  aws ecr create-repository \
    --repository-name $ECR_REPOSITORY \
    --region $AWS_REGION \
    --image-scanning-configuration scanOnPush=true \
    --encryption-configuration encryptionType=AES256
else
  echo "   ✓ Repository exists"
fi

# Step 2: Login to ECR
echo "🔐 Logging into ECR..."
aws ecr get-login-password --region $AWS_REGION | \
  docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

# Step 3: Build Docker image
echo "🔨 Building Docker image..."
docker build -t $ECR_REPOSITORY:latest .

# Step 4: Tag image
ECR_IMAGE_URI="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY:latest"
echo "🏷️  Tagging image as $ECR_IMAGE_URI"
docker tag $ECR_REPOSITORY:latest $ECR_IMAGE_URI

# Step 5: Push image to ECR
echo "📤 Pushing image to ECR..."
docker push $ECR_IMAGE_URI

# Step 6: Get App Runner service ARN
echo "🔍 Looking up App Runner service..."
SERVICE_ARN=$(aws apprunner list-services \
  --region $AWS_REGION \
  --query "ServiceSummaryList[?ServiceName=='$APP_RUNNER_SERVICE'].ServiceArn" \
  --output text 2>/dev/null || echo "")

if [ -z "$SERVICE_ARN" ]; then
  echo ""
  echo "⚠️  App Runner service '$APP_RUNNER_SERVICE' not found!"
  echo "   Please create the service first in AWS Console:"
  echo "   https://console.aws.amazon.com/apprunner"
  echo ""
  echo "   Or use the CLI (see README-DEPLOYMENT.md for details)"
  echo ""
  echo "✅ Image pushed successfully to ECR:"
  echo "   Image URI: $ECR_IMAGE_URI"
  exit 0
fi

echo "   ✓ Found service: $SERVICE_ARN"

# Step 7: Check if auto-deploy is enabled
echo "🔍 Checking auto-deployment settings..."
AUTO_DEPLOY=$(aws apprunner describe-service \
  --service-arn $SERVICE_ARN \
  --region $AWS_REGION \
  --query 'Service.SourceConfiguration.AutoDeploymentsEnabled' \
  --output text 2>/dev/null || echo "false")

if [ "$AUTO_DEPLOY" = "true" ]; then
  echo "   ✓ Auto-deployment is enabled"
  echo "   App Runner will automatically detect the new image and deploy"
  echo ""
  echo "✅ Image pushed successfully!"
  echo "   Image URI: $ECR_IMAGE_URI"
  echo "   Deployment will start automatically in a few moments"
  echo ""
  echo "📊 Monitor deployment:"
  echo "   aws apprunner describe-service --service-arn $SERVICE_ARN --region $AWS_REGION"
else
  echo "   ⚠️  Auto-deployment is disabled"
  echo "   Triggering manual deployment..."
  
  # Check current image configuration
  CURRENT_IMAGE=$(aws apprunner describe-service \
    --service-arn $SERVICE_ARN \
    --region $AWS_REGION \
    --query 'Service.SourceConfiguration.ImageRepository.ImageIdentifier' \
    --output text 2>/dev/null || echo "")
  
  # If service is configured to use 'latest' tag, it will pick up the new image
  # Otherwise, we need to update the service configuration
  if [[ "$CURRENT_IMAGE" == *":latest" ]] || [[ "$CURRENT_IMAGE" == "$ECR_IMAGE_URI" ]]; then
    echo "   ✓ Service is configured to use latest image"
    # Just trigger deployment - it will use the latest image
    DEPLOYMENT_ID=$(aws apprunner start-deployment \
      --service-arn $SERVICE_ARN \
      --region $AWS_REGION \
      --query 'OperationId' \
      --output text 2>/dev/null || echo "")
    
    if [ -n "$DEPLOYMENT_ID" ]; then
      echo ""
      echo "✅ Deployment triggered!"
      echo "   Image URI: $ECR_IMAGE_URI"
      echo "   Deployment ID: $DEPLOYMENT_ID"
    else
      echo ""
      echo "⚠️  Could not trigger deployment automatically"
      echo "   Please trigger manually in AWS Console or update service configuration"
    fi
  else
    echo "   ⚠️  Service image doesn't match. Current: $CURRENT_IMAGE"
    echo "   Please update service configuration in AWS Console to use: $ECR_IMAGE_URI"
    echo "   Or run this command to update:"
    echo "   aws apprunner update-service --service-arn $SERVICE_ARN --source-configuration '...'"
  fi
  
  echo ""
  echo "📊 Monitor deployment:"
  echo "   aws apprunner describe-service --service-arn $SERVICE_ARN --region $AWS_REGION"
fi

echo ""
echo "🌐 Service URL:"
SERVICE_URL=$(aws apprunner describe-service \
  --service-arn $SERVICE_ARN \
  --region $AWS_REGION \
  --query 'Service.ServiceUrl' \
  --output text 2>/dev/null || echo "N/A")
echo "   $SERVICE_URL"

