# AWS App Runner Deployment Guide

This guide walks you through deploying the Palabam FastAPI backend to AWS App Runner.

## Prerequisites

1. **AWS CLI** installed and configured with appropriate credentials
   ```bash
   aws --version
   aws configure
   ```

2. **Docker** installed and running
   ```bash
   docker --version
   ```

3. **AWS Permissions** - Your IAM user/role needs:
   - `ecr:*` (Elastic Container Registry)
   - `apprunner:*` (App Runner service management)
   - `iam:PassRole` (for App Runner service role)
   - `secretsmanager:*` (if using Secrets Manager for env vars)

## Initial Setup (First Time Only)

### 1. Create ECR Repository

The deployment script will create this automatically, but you can also create it manually:

```bash
aws ecr create-repository \
  --repository-name palabam-backend \
  --region us-east-1 \
  --image-scanning-configuration scanOnPush=true
```

### 2. Create App Runner Service

#### Option A: Using AWS Console (Recommended for first setup)

1. Go to [AWS App Runner Console](https://console.aws.amazon.com/apprunner)
2. Click "Create service"
3. Choose "Container registry" → "Amazon ECR"
4. Select your ECR repository: `palabam-backend`
5. Select image tag: `latest`
6. Configure service:
   - **Service name**: `palabam-backend`
   - **Virtual CPU**: 1 vCPU (or 2 for better performance)
   - **Memory**: 2 GB (or 4 GB for NLP workloads)
   - **Port**: `8000`
   - **Health check path**: `/health`
7. Set environment variables:
   - `SUPABASE_URL` = Your Supabase project URL
   - `SUPABASE_KEY` = Your Supabase service role key
   - `AWS_ACCESS_KEY_ID` = Your AWS access key (for Transcribe)
   - `AWS_SECRET_ACCESS_KEY` = Your AWS secret key
   - `AWS_REGION` = `us-east-1`
8. Configure auto-scaling (optional):
   - Min: 1, Max: 10
   - Target CPU: 70%
9. Review and create

#### Option B: Using AWS CLI

First, create an IAM role for App Runner:

```bash
# Create trust policy
cat > apprunner-trust-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "build.apprunner.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

# Create access policy (for ECR and CloudWatch)
cat > apprunner-access-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ecr:GetAuthorizationToken",
        "ecr:BatchCheckLayerAvailability",
        "ecr:GetDownloadUrlForLayer",
        "ecr:BatchGetImage",
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "*"
    }
  ]
}
EOF

# Create role
aws iam create-role \
  --role-name AppRunnerServiceRole \
  --assume-role-policy-document file://apprunner-trust-policy.json

aws iam put-role-policy \
  --role-name AppRunnerServiceRole \
  --policy-name AppRunnerAccessPolicy \
  --policy-document file://apprunner-access-policy.json
```

Then create the service:

```bash
# Get ECR repository URI
ECR_URI=$(aws ecr describe-repositories \
  --repository-names palabam-backend \
  --region us-east-1 \
  --query 'repositories[0].repositoryUri' \
  --output text)

# Create App Runner service
aws apprunner create-service \
  --service-name palabam-backend \
  --source-configuration "{
    \"ImageRepository\": {
      \"ImageIdentifier\": \"$ECR_URI:latest\",
      \"ImageConfiguration\": {
        \"Port\": \"8000\",
        \"RuntimeEnvironmentVariables\": {
          \"SUPABASE_URL\": \"your-supabase-url\",
          \"SUPABASE_KEY\": \"your-supabase-key\",
          \"AWS_ACCESS_KEY_ID\": \"your-aws-key\",
          \"AWS_SECRET_ACCESS_KEY\": \"your-aws-secret\",
          \"AWS_REGION\": \"us-east-1\"
        }
      },
      \"ImageRepositoryType\": \"ECR\"
    },
    \"AutoDeploymentsEnabled\": false
  }" \
  --instance-configuration "{
    \"Cpu\": \"1 vCPU\",
    \"Memory\": \"2 GB\"
  }" \
  --health-check-configuration "{
    \"Protocol\": \"HTTP\",
    \"Path\": \"/health\",
    \"Interval\": 10,
    \"Timeout\": 5,
    \"HealthyThreshold\": 1,
    \"UnhealthyThreshold\": 5
  }" \
  --auto-scaling-configuration-arn <your-auto-scaling-config-arn> \
  --region us-east-1
```

### 3. Store Secrets in AWS Secrets Manager (Optional but Recommended)

Instead of storing secrets in environment variables, use Secrets Manager:

```bash
# Create secrets
aws secretsmanager create-secret \
  --name palabam/supabase-url \
  --secret-string "https://your-project.supabase.co" \
  --region us-east-1

aws secretsmanager create-secret \
  --name palabam/supabase-key \
  --secret-string "your-service-role-key" \
  --region us-east-1

aws secretsmanager create-secret \
  --name palabam/aws-access-key-id \
  --secret-string "your-aws-access-key-id" \
  --region us-east-1

aws secretsmanager create-secret \
  --name palabam/aws-secret-access-key \
  --secret-string "your-aws-secret-access-key" \
  --region us-east-1
```

Then reference them in App Runner service configuration.

## Deployment Process

### Automated Deployment

1. Make the script executable:
   ```bash
   chmod +x deploy.sh
   ```

2. Run the deployment script:
   ```bash
   ./deploy.sh
   ```

3. Update App Runner service to use the new image:
   - Go to App Runner Console
   - Select your service
   - Click "Deploy new revision"
   - Or use AWS CLI (see below)

### Manual Deployment Steps

1. **Build and push Docker image:**
   ```bash
   # Build
   docker build -t palabam-backend:latest .
   
   # Tag
   docker tag palabam-backend:latest \
     <account-id>.dkr.ecr.us-east-1.amazonaws.com/palabam-backend:latest
   
   # Login to ECR
   aws ecr get-login-password --region us-east-1 | \
     docker login --username AWS --password-stdin \
     <account-id>.dkr.ecr.us-east-1.amazonaws.com
   
   # Push
   docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/palabam-backend:latest
   ```

2. **Trigger App Runner deployment:**
   ```bash
   # Get service ARN
   SERVICE_ARN=$(aws apprunner list-services \
     --region us-east-1 \
     --query "ServiceSummaryList[?ServiceName=='palabam-backend'].ServiceArn" \
     --output text)
   
   # Start deployment
   aws apprunner start-deployment \
     --service-arn $SERVICE_ARN \
     --region us-east-1
   ```

## Updating Environment Variables

### Via AWS Console

1. Go to App Runner Console
2. Select your service
3. Go to "Configuration" tab
4. Click "Edit"
5. Update environment variables
6. Save and deploy

### Via AWS CLI

```bash
# Get current service configuration
aws apprunner describe-service \
  --service-arn <your-service-arn> \
  --region us-east-1 > service-config.json

# Edit service-config.json to update environment variables
# Then update service:
aws apprunner update-service \
  --service-arn <your-service-arn> \
  --source-configuration file://service-config.json \
  --region us-east-1
```

## Monitoring and Logs

### View Logs

```bash
# Get log group name
LOG_GROUP="/aws/apprunner/palabam-backend"

# Tail logs
aws logs tail $LOG_GROUP --follow --region us-east-1
```

### View Service Status

```bash
aws apprunner describe-service \
  --service-arn <your-service-arn> \
  --region us-east-1
```

### View Metrics

- Go to CloudWatch Console
- Navigate to "Metrics" → "AWS/AppRunner"
- Select your service metrics

## Getting Your Service URL

After deployment, get your service URL:

```bash
aws apprunner describe-service \
  --service-arn <your-service-arn> \
  --region us-east-1 \
  --query 'Service.ServiceUrl' \
  --output text
```

Or find it in the AWS Console under your App Runner service.

## Updating Frontend Configuration

Once deployed, update your frontend to point to the App Runner URL:

1. Get your App Runner service URL (see above)
2. Update `frontend/.env` or environment variables:
   ```
   NUXT_PUBLIC_API_URL=https://your-service-id.us-east-1.awsapprunner.com
   ```

## Cost Optimization

- **Auto-scaling**: Set appropriate min/max instances
- **Instance size**: Start with 1 vCPU / 2 GB, scale up if needed
- **Health checks**: Proper health checks prevent unnecessary restarts
- **Idle timeout**: Configure appropriate timeout for your workload

## Troubleshooting

### Service fails to start

1. Check CloudWatch logs:
   ```bash
   aws logs tail /aws/apprunner/palabam-backend --follow
   ```

2. Verify environment variables are set correctly

3. Check health check endpoint is accessible: `/health`

4. Verify Docker image builds successfully locally:
   ```bash
   docker build -t test-palabam .
   docker run -p 8000:8000 test-palabam
   ```

### High latency

- Increase instance size (CPU/memory)
- Enable connection pooling
- Check if cold starts are the issue (keep min instances > 0)

### Out of memory errors

- Increase memory allocation (up to 4 GB)
- Check spaCy model size
- Optimize Docker image

### Image pull errors

- Verify ECR repository exists
- Check IAM permissions for App Runner service role
- Verify image tag is correct

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Deploy to App Runner

on:
  push:
    branches: [main]
    paths:
      - 'backend/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
      
      - name: Login to ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v1
      
      - name: Build and push Docker image
        env:
          ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
          ECR_REPOSITORY: palabam-backend
          IMAGE_TAG: latest
        run: |
          docker build -t $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG ./backend
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG
      
      - name: Deploy to App Runner
        run: |
          SERVICE_ARN=$(aws apprunner list-services \
            --region us-east-1 \
            --query "ServiceSummaryList[?ServiceName=='palabam-backend'].ServiceArn" \
            --output text)
          aws apprunner start-deployment \
            --service-arn $SERVICE_ARN \
            --region us-east-1
```

## Next Steps

1. ✅ Set up App Runner service (first time)
2. ✅ Run initial deployment
3. ✅ Get service URL
4. ✅ Update frontend `NUXT_PUBLIC_API_URL`
5. ✅ Test endpoints
6. ✅ Set up monitoring/alarms
7. ✅ Configure auto-scaling
8. ✅ Set up CI/CD pipeline (optional)



