# Deployment Workflow: How Backend Updates Work

This document explains how your local code changes get deployed to AWS App Runner.

## Quick Answer

**To deploy your local changes:**
```bash
cd backend
./deploy.sh
```

That's it! The script will:
1. Build a new Docker image with your changes
2. Push it to AWS ECR
3. Automatically trigger App Runner to deploy the new version

## Complete Workflow

### 1. Make Local Changes

Edit your code in `backend/`:
- Modify Python files (`main.py`, `api/*.py`, `nlp/*.py`, etc.)
- Update `requirements.txt` if needed
- Add new files

### 2. Deploy

Run the deployment script:
```bash
cd backend
./deploy.sh
```

**What happens:**
1. ✅ Builds Docker image with your changes
2. ✅ Pushes to AWS ECR (Elastic Container Registry)
3. ✅ Automatically triggers App Runner deployment
4. ✅ Shows you the service URL

### 3. App Runner Deploys

App Runner will:
- Pull the new image from ECR
- Start new instances with your updated code
- Health check the new instances
- Route traffic to new instances (zero-downtime)
- Shut down old instances

**Deployment time:** Usually 2-5 minutes

## Two Deployment Modes

### Option A: Auto-Deploy (Recommended - Easiest)

When you create your App Runner service, enable **"Auto deployments"**.

**How it works:**
1. You run `./deploy.sh`
2. Script pushes new image to ECR
3. App Runner **automatically detects** the new image
4. App Runner **automatically starts** deployment
5. You're done! 🎉

**Setup:** Enable "Auto deployments" when creating the service in AWS Console.

### Option B: Manual Deploy

If auto-deploy is disabled, the script will:
1. Push image to ECR
2. **Automatically trigger** deployment via AWS CLI
3. You're done! 🎉

**Note:** The script handles this automatically, so you still just run `./deploy.sh`

## Step-by-Step Example

Let's say you update the health check endpoint:

```bash
# 1. Edit the code
vim backend/main.py
# Change: return {"status": "healthy", "version": "2.0.0"}

# 2. Test locally (optional)
cd backend
source venv/bin/activate
uvicorn main:app --reload
# Test at http://localhost:8000/health

# 3. Deploy
./deploy.sh

# Output:
# 🚀 Deploying Palabam Backend to AWS App Runner
# 📦 Checking ECR repository...
#    ✓ Repository exists
# 🔐 Logging into ECR...
# 🔨 Building Docker image...
# 🏷️  Tagging image...
# 📤 Pushing image to ECR...
# 🔍 Looking up App Runner service...
#    ✓ Found service: arn:aws:apprunner:...
# 🔍 Checking auto-deployment settings...
#    ✓ Auto-deployment is enabled
# ✅ Image pushed successfully!
#    Deployment will start automatically in a few moments
# 🌐 Service URL: https://xxxxx.us-east-1.awsapprunner.com
```

**That's it!** Your changes are live in 2-5 minutes.

## Monitoring Deployments

### Check Deployment Status

```bash
# Get service ARN first
SERVICE_ARN=$(aws apprunner list-services \
  --region us-east-1 \
  --query "ServiceSummaryList[?ServiceName=='palabam-backend'].ServiceArn" \
  --output text)

# Check status
aws apprunner describe-service \
  --service-arn $SERVICE_ARN \
  --region us-east-1 \
  --query 'Service.Status'
```

### View Logs

```bash
# Tail logs in real-time
aws logs tail /aws/apprunner/palabam-backend --follow --region us-east-1
```

### Check Service Health

```bash
# Get service URL
SERVICE_URL=$(aws apprunner describe-service \
  --service-arn $SERVICE_ARN \
  --region us-east-1 \
  --query 'Service.ServiceUrl' \
  --output text)

# Test health endpoint
curl $SERVICE_URL/health
```

## Common Scenarios

### Scenario 1: Quick Bug Fix

```bash
# Fix bug
vim backend/api/students.py

# Deploy
./deploy.sh

# Done! Changes live in ~3 minutes
```

### Scenario 2: Adding New Dependencies

```bash
# Add to requirements.txt
echo "new-package==1.0.0" >> backend/requirements.txt

# Deploy (Dockerfile will install new package)
./deploy.sh
```

### Scenario 3: Updating Environment Variables

**Via AWS Console:**
1. Go to App Runner Console
2. Select your service
3. Configuration → Edit
4. Update environment variables
5. Save (triggers new deployment)

**Via CLI:**
```bash
# See README-DEPLOYMENT.md for full example
aws apprunner update-service \
  --service-arn <your-arn> \
  --source-configuration file://config.json
```

## CI/CD Integration (Optional)

For automatic deployments on git push, see `README-DEPLOYMENT.md` for GitHub Actions example.

**Workflow:**
1. Push code to GitHub
2. GitHub Actions runs automatically
3. Builds and deploys to App Runner
4. Your changes are live!

## Troubleshooting

### Deployment Fails

1. **Check logs:**
   ```bash
   aws logs tail /aws/apprunner/palabam-backend --follow
   ```

2. **Verify Docker image builds locally:**
   ```bash
   docker build -t test-palabam ./backend
   docker run -p 8000:8000 test-palabam
   ```

3. **Check App Runner service status:**
   ```bash
   aws apprunner describe-service --service-arn <arn>
   ```

### Changes Not Appearing

1. **Verify deployment completed:**
   - Check App Runner console
   - Look for "Deployment successful" status

2. **Check you're hitting the right URL:**
   - App Runner URL might have changed
   - Get current URL: `aws apprunner describe-service ...`

3. **Clear browser cache** (if frontend caching)

### Slow Deployments

- First deployment: 5-10 minutes (pulling base images)
- Subsequent deployments: 2-5 minutes
- If slower, check CloudWatch metrics for resource constraints

## Best Practices

1. **Test locally first:**
   ```bash
   cd backend
   source venv/bin/activate
   uvicorn main:app --reload
   ```

2. **Use version tags for production:**
   - Instead of `latest`, use version tags: `v1.0.0`, `v1.0.1`
   - Update deploy script to use version tags

3. **Monitor after deployment:**
   - Check health endpoint
   - Monitor logs for errors
   - Verify functionality

4. **Keep deployments small:**
   - Deploy frequently with small changes
   - Easier to debug if something breaks

## Summary

**The Simple Answer:**
- Make changes locally
- Run `./deploy.sh`
- Wait 2-5 minutes
- Your changes are live! 🚀

The deployment script handles everything automatically, so you don't need to worry about the details unless something goes wrong.



