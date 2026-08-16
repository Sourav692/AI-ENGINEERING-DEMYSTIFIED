# Deployment Guide

This guide details how to deploy the **rag_voice_ai_agent** application, starting from local development to a full AWS production deployment using ECS Fargate and CloudFormation.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development](#local-development)
3. [AWS Production Deployment](#aws-production-deployment)
4. [CI/CD Pipeline](#cicd-pipeline)
5. [Managing Secrets & Updates](#managing-secrets--updates)
6. [Troubleshooting & Known Issues](#troubleshooting--known-issues)

---

## Prerequisites

### Required Services

1. **MongoDB Atlas**
   - Create a Cluster.
   - Create a database (e.g., `rag_voice_agent_db`).
   - Allow access from anywhere `0.0.0.0/0` (for initial testing) or configure specific whitelist IPs later.
   - **Vector Search Index**: Create an index named `vector_index` on your chunks collection.

2. **API Keys**
   - [Deepgram API Key](https://console.deepgram.com/) - for Speech-to-Text.
   - [ElevenLabs API Key](https://elevenlabs.io/) - for Text-to-Speech.
   - [Groq API Key](https://console.groq.com/) - for Llama 3 inference.
   - [Google AI API Key](https://aistudio.google.com/) - for Gemini Embeddings.

3. **Tools**
   - [Docker Desktop](https://www.docker.com/products/docker-desktop/)
   - [AWS CLI](https://aws.amazon.com/cli/) version 2+
   - [Git](https://git-scm.com/)

---

## Local Development

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd rag_voice_ai_agent
   ```

2. **Environment Setup**
   Create a `.env` file in the `backend/` directory:
   ```env
   MONGO_URL=mongodb+srv://<user>:<password>@<cluster>.mongodb.net
   DB_NAME=rag_voice_agent_db
   DEEPGRAM_API_KEY=your_key
   ELEVENLABS_API_KEY=your_key
   GROQ_API_KEY=your_key
   GOOGLE_API_KEY=your_key
   ```

3. **Run with Docker Compose**
   ```bash
   docker-compose up --build
   ```
   - Frontend: http://localhost:5173
   - Backend: http://localhost:8000
   - API Docs: http://localhost:8000/docs

---

## AWS Production Deployment

We use **Amazon ECS (Fargate)** with an **Application Load Balancer (ALB)**. Infrastructure is provisioned via **CloudFormation**.

### Step 1: AWS Account & CLI Setup

1. **Create an AWS Account** if you don't have one.
2. **Install AWS CLI** and configure it:
   ```bash
   aws configure
   # Enter your Access Key ID, Secret Access Key, Region (e.g., us-east-1), and output format (json).
   ```

### Step 1.1: Required IAM Permissions

The AWS user or profile you use to run the setup scripts and CI/CD pipeline must have the following permissions. Because CloudFormation creates IAM Roles and specific network infrastructure, **AdminAccess** is recommended for the initial setup.

If you need a restricted policy, ensure the user has:

**Managed Policies:**
- `AWSCloudFormationFullAccess`
- `AmazonECS_FullAccess`
- `AmazonEC2FullAccess`
- `AmazonEC2ContainerRegistryFullAccess`
- `SecretsManagerReadWrite`
- `IAMFullAccess` (Required to create Execution/Task Roles)

**Custom Policy (Minimum Required Actions):**
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "cloudformation:*",
                "ec2:*",
                "ecs:*",
                "ecr:*",
                "elasticloadbalancing:*",
                "iam:CreateRole",
                "iam:DeleteRole",
                "iam:AttachRolePolicy",
                "iam:DetachRolePolicy",
                "iam:PutRolePolicy",
                "iam:DeleteRolePolicy",
                "iam:GetRole",
                "iam:PassRole",
                "secretsmanager:CreateSecret",
                "secretsmanager:GetSecretValue",
                "secretsmanager:DescribeSecret",
                "secretsmanager:DeleteSecret",
                "logs:CreateLogGroup",
                "logs:DeleteLogGroup",
                "logs:PutRetentionPolicy"
            ],
            "Resource": "*"
        }
    ]
}
```
> [!WARNING]
> The `iam:PassRole` permission is critical. It allows the deployment user to assign the `ECSExecutionRole` and `ECSTaskRole` to the ECS Tasks. without it, deployments will fail.

### Step 2: Infrastructure Provisioning

We have automated scripts to set up the VPC, ECR, ECS Cluster, and Secrets.

1. **Navigate to Infrastructure Directory**
   ```bash
   cd infrastructure
   ```

2. **Run Setup Script**
   ```bash
   chmod +x setup-aws.sh
   ./setup-aws.sh
   ```
   - This script will prompt you for your API keys (Deepgram, ElevenLabs, Groq, Google, Mongo) to securely store them in **AWS Secrets Manager**.
   - It will trigger the CloudFormation stack creation.
   - **Wait** for the stack to reach `CREATE_COMPLETE` status (approx. 5-10 mins).

3. **Note Outputs**
   The script will output critical values. Note down:
   - `ALBDNSName` (The URL of your app)
   - `BackendRepoUrl`
   - `FrontendRepoUrl`
   - `ClusterName`

### Step 2.1: Update AWS Account ID in Configuration

The Task Definition files in this repository may contain a hardcoded AWS Account ID (e.g., `306570692493`) that acts as a placeholder or belongs to the original template. You **must** replace this with your own AWS Account ID.

1.  **Get your AWS Account ID**:
    ```bash
    aws sts get-caller-identity --query Account --output text
    ```

2.  **Update Configuration Files**:
    Open the following files and replace the placeholder ID with your actual Account ID in all ARNs (Amazon Resource Names) and Image URIs:

    -   `.github/workflows/task-definition-backend.json`
    -   `.github/workflows/task-definition-frontend.json`

    *Fields to check:* `executionRoleArn`, `taskRoleArn`, `image`, and `valueFrom` (Secrets Manager ARNs).

### Step 3: Configure GitHub Secrets

**Before pushing any code**, you must configure your GitHub repository secrets so the CI/CD pipeline can authenticate with AWS.

Go to your **GitHub Repository -> Settings -> Secrets and variables -> Actions -> New repository secret**.

Add the following secrets (values from Step 2 outputs):

| Secret Name | Value Description |
|---|---|
| `AWS_ACCESS_KEY_ID` | Your AWS Access Key ID |
| `AWS_SECRET_ACCESS_KEY` | Your AWS Secret Access Key |
| `AWS_REGION` | `us-east-1` (or your chosen region) |
| `ECR_REPOSITORY_BACKEND` | **Repository Name** (e.g., `rag-voice-agent-backend`) **NOT the full URL** |
| `ECR_REPOSITORY_FRONTEND` | **Repository Name** (e.g., `rag-voice-agent-frontend`) **NOT the full URL** |
| `ECS_SERVICE_BACKEND` | `rag-voice-agent-backend-service` |
| `ECS_SERVICE_FRONTEND` | `rag-voice-agent-frontend-service` |
| `ECS_CLUSTER` | **ClusterName** (e.g., `rag-voice-agent-cluster`) |
| `ECS_TASK_DEFINITION_BACKEND` | `.github/workflows/task-definition-backend.json` |
| `ECS_TASK_DEFINITION_FRONTEND` | `.github/workflows/task-definition-frontend.json` |
| `CONTAINER_NAME_BACKEND` | `rag-voice-agent-backend-container` |
| `CONTAINER_NAME_FRONTEND` | `rag-voice-agent-frontend-container` |

### Step 4: Trigger Initial Deployment (CI/CD)

1.  **Commit and Push** your code to the `main` branch.
2.  Go to the **Actions** tab in your GitHub repository.
3.  **Expect Failure**: The "Deploy" step will fail initially because the ECS Services do not exist yet. This is normal.
4.  **Success Check**: Ensure the "Build and Push" steps passed. This means your Docker images are successfully in ECR.

### Step 5: Create ECS Services

Once the images are in ECR and Task Definitions are registered (via the CI/CD run), create the actual ECS Services:

1.  **Register Frontend Task Definition manually (if missing)**:
    ```bash
    aws ecs register-task-definition --cli-input-json file://.github/workflows/task-definition-frontend.json
    ```

2.  **Run Creation Script**:
    ```bash
    chmod +x scripts/create-services.sh
    ./scripts/create-services.sh
    ```

3.  **Finish Deployment**:
    - Go back to GitHub Actions and re-run the failed job, or simply push a small change to `main`. The deployment should now succeed completely.

### Step 6: Fix IAM Permissions (One-time)

Ensure ECS tasks can access the Secrets Manager:

```bash
chmod +x fix-iam-permissions.sh
./fix-iam-permissions.sh
```

---

## Deployment Complete!

Your application should now be live at the **ALBDNSName** URL you noted in Step 2.

---

## Managing Secrets & Updates

### Updating API Keys
If you change an API key (e.g., new Groq key), you **do not** need to rebuild the Docker image.

1.  **Update Secret in AWS**:
    - Go to **AWS Secrets Manager** -> `rag-voice-agent-secrets`.
    - Click **Retrieve secret value** -> **Edit**.
    - Update the value and **Save**.

2.  **Force Deployment**:
    - Run the deployment script to restart containers and pick up new secrets:
      ```bash
      chmod +x scripts/deploy_aws.sh
      ./scripts/deploy_aws.sh
      ```
    - Or run manually:
      ```bash
      aws ecs update-service --cluster rag-voice-agent-cluster --service rag-voice-agent-backend-service --force-new-deployment
      ```

---

## Troubleshooting & Known Issues

### 1. 401 Invalid API Key Error
**Symptoms**: The bot connects but immediately disconnects with an "Invalid API Key" error in the logs.
**Cause**: The API key in AWS Secrets Manager is missing, empty, or has whitespace.
**Fix**:
- **Check Task Definition**: Ensure `task-definition-backend.json` maps the secret environment variable correctly (e.g., `ELEVENLABS_API_KEY`).
- **Check Secrets Manager**: Verify the key name matches exactly (e.g., `ELEVENLABS_API_KEY` vs `ELEVEN_LABS_API_KEY`).
- **Restart Service**: You MUST force a new deployment for changes to take effect.

### 2. Microphone Not Working (insecure Context)
**Symptoms**: Browser blocks microphone access when visiting the ALB URL (`http://...`).
**Cause**: Browsers usually require HTTPS for microphone access.
**Workaround (Testing only)**:
1.  Go to `chrome://flags` (or `edge://flags`).
2.  Enable **"Insecure origins treated as secure"**.
3.  Add your ALB URL (e.g., `http://rag-voice-agent-alb-....elb.amazonaws.com`).
4.  Relaunch browser.

### 3. Frontend Build Failure "Could not load ..."
**Symptoms**: Docker build fails with `Could not load /app/src/lib/api`.
**Cause**: File permission/context issues with specific directory names in Docker.
**Fix**:
- We moved `src/lib/api.ts` to `src/utils/api.ts` to resolve this. Ensure imports use `../utils/api`.

### 4. "CannotPullContainerError"
**Symptoms**: ECS tasks fail to start.
**Cause**: The Docker image was not pushed to ECR, or the IAM Role lacks permission.
**Fix**:
- Check GitHub Actions logs to ensure "Build and Push" Step succeeded.
- Ensure `ECSExecutionRole` has `AmazonECSTaskExecutionRolePolicy`.