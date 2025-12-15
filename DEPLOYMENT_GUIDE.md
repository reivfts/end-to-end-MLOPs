# 🚀 Campus Services Hub - Deployment Guide

## For Team Members

This document explains our CI/CD pipeline and AWS infrastructure setup.

---

## 📍 Live Application

**URL:** http://3.141.167.20:5001

> ⚠️ **Note:** The public IP changes when containers restart. Check the ECS Console for the current IP.

---

## 🔄 How CI/CD Works


### Current Configuration
- **Trigger Branch:** `cleaned-architecture`
- **Image Naming:** Only images with the `-cleaned-architecture` tag (e.g., `gateway-cleaned-architecture`) are built and deployed to ECS. This keeps deployments clear and branch-specific.
- **Important:** When moving to production, update image tags and task definitions to use `main` (e.g., `gateway-main`).
- **Future Change Needed:** Update to `main` branch and image tags before production

### What Happens When You Push Code

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Git Push  │ ──► │   GitHub    │ ──► │  Build &    │ ──► │  Deploy to  │
│  to branch  │     │   Actions   │     │  Push ECR   │     │    ECS      │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
```

1. **Push to `cleaned-architecture`** → Triggers GitHub Actions
2. **Build Phase** → Docker images built for each service
3. **Push to ECR** → Images stored in AWS container registry
4. **Deploy to ECS** → Services automatically restart with new images

### Deployment Time
- Build: ~3-5 minutes
- Deploy: ~2-3 minutes
- **Total: ~5-10 minutes** after push

---

## 📁 Key Files

| File | Purpose |
|------|---------|
| `.github/workflows/docker-publish.yml` | CI/CD pipeline definition |
| `ecs/task-definition-*.json` | Container configurations for each service |

---

## 🏗️ AWS Infrastructure

### Services Running

| Service | Port | Purpose |
|---------|------|---------|
| Gateway | 5001 | API Gateway & Frontend |
| PostgreSQL | 5432 | Database |
| User Management | 8002 | User auth & management |
| Booking | 8000 | Room booking system |
| GPA Calculator | 8003 | GPA calculations |
| Notification | 8004 | Notifications |
| Maintenance | 8080 | Maintenance requests |

### AWS Resources

| Resource | Value |
|----------|-------|
| Region | `us-east-2` (Ohio) |
| ECS Cluster | `UNIVERSITY_SERVICES_HUB` |
| ECR Repository | `campus-services-hubs` |
| Service Discovery | `*.campus-services.local` |

---

## 🔧 Before Merging to Main

### Required Changes

Edit `.github/workflows/docker-publish.yml`:

```yaml
# CHANGE FROM:
on:
  push:
    branches:
      - cleaned-architecture

# CHANGE TO:
on:
  push:
    branches:
      - main
```

Also update **all task definitions** in `ecs/` folder:

```json
// CHANGE FROM:
"image": "643771447281.dkr.ecr.us-east-2.amazonaws.com/campus-services-hubs:gateway-cleaned-architecture"

// CHANGE TO:
"image": "643771447281.dkr.ecr.us-east-2.amazonaws.com/campus-services-hubs:gateway-main"
```

---

## 🔍 How to Check Deployment Status

### Option 1: GitHub Actions
1. Go to repo → **Actions** tab
2. Check latest workflow run status

### Option 2: AWS Console
1. Go to **ECS** → **Clusters** → `UNIVERSITY_SERVICES_HUB`
2. Click **Services** → Check each service's **Running Count**

### Option 3: AWS CLI
```bash
aws ecs describe-services \
  --cluster UNIVERSITY_SERVICES_HUB \
  --services gateway-service \
  --region us-east-2 \
  --query "services[0].[runningCount,desiredCount]"
```

---

## 🌐 Getting the Current Public IP

The gateway's public IP changes on each deployment. To find it:

### Via AWS Console
1. ECS → Clusters → `UNIVERSITY_SERVICES_HUB`
2. Click **Tasks** tab
3. Click the gateway task
4. Under **Network** → Find **Public IP**

### Via AWS CLI
```bash
# Get task ARN
aws ecs list-tasks --cluster UNIVERSITY_SERVICES_HUB --service-name gateway-service --region us-east-2

# Get task details (replace TASK_ARN)
aws ecs describe-tasks --cluster UNIVERSITY_SERVICES_HUB --tasks TASK_ARN --region us-east-2 --query "tasks[0].attachments[0].details"
```

---

## 🔐 Required GitHub Secrets

These secrets are already configured in the repo:

| Secret | Description |
|--------|-------------|
| `AWS_ACCESS_KEY_ID` | AWS IAM access key |
| `AWS_SECRET_ACCESS_KEY` | AWS IAM secret key |

---

## 🐛 Troubleshooting

### Container keeps restarting
Check CloudWatch logs:
1. AWS Console → CloudWatch → Log Groups
2. Look for `/ecs/service-name`

### Service unavailable
1. Check if all services are running in ECS
2. Verify security group allows traffic
3. Check service logs for errors

### Database connection failed
Services connect via Cloud Map DNS: `postgres.campus-services.local`
- Ensure postgres service is running first

---

## 📞 Need Help?

If you encounter issues:
1. Check GitHub Actions logs first
2. Check CloudWatch logs for the specific service
3. Verify all 7 services are running in ECS console

---

*Last updated: December 15, 2025*
