# JobLens AI — AWS Production Deployment Guide

This guide walks you step-by-step through deploying **JobLens AI** to AWS for the **AWS Weekend Creative Challenge**.

---

## 🏗️ Production Architecture

```text
                                  End User
                                     │
                                     ▼ HTTPS
                           ┌───────────────────┐
                           │    AWS Amplify    │  (Hosts React/Vite SPA)
                           └─────────┬─────────┘
                                     │
                                     ▼ HTTPS (VITE_API_BASE_URL)
                           ┌───────────────────┐
                           │ Amazon API Gateway│  (HTTP API - Proxy Router)
                           └─────────┬─────────┘
                                     │
                                     ▼
                           ┌───────────────────┐
                           │    AWS Lambda     │  (FastAPI + Mangum Adapter)
                           │ (Python 3.12/3.13)│  (In-Memory PDF Extraction)
                           └─────────┬─────────┘
                                     │
                                     ▼ Boto3 Converse API (IAM Role)
                           ┌───────────────────┐
                           │   Amazon Bedrock  │  (Nova 2 Lite Inference)
                           │(us.amazon.nova-2) │
                           └───────────────────┘
```

---

## 📋 Summary of Required AWS Resources

| AWS Service | Resource Name / Identifier | Purpose |
|---|---|---|
| **AWS Lambda** | `joblens-ai-backend` | Runs the FastAPI application via `lambda_handler.handler` |
| **IAM Role** | `joblens-ai-lambda-role` | Grants Lambda execution permissions and Amazon Bedrock access |
| **Amazon API Gateway** | `joblens-ai-api` (HTTP API) | Exposes public HTTPS endpoint routing to the Lambda function |
| **AWS Amplify** | `joblens-ai-frontend` | Builds and hosts the React + Vite single-page application |
| **Amazon Bedrock** | `us.amazon.nova-2-lite-v1:0` | Serverless AI inference profile for analysis and interview coaching |

---

## 🚀 Step-by-Step Deployment Instructions

### STEP 1: Deploy Backend to AWS Lambda

1. **Package the backend directory**:
   - Create a deployment ZIP package containing the `app/` folder, `lambda_handler.py`, and installed Python dependencies from `requirements.txt`.
2. **Open AWS Console → Lambda**:
   - Click **Create function** → Choose **Author from scratch**.
   - **Function name**: `joblens-ai-backend`
   - **Runtime**: `Python 3.12` or `Python 3.13`
   - **Architecture**: `x86_64` or `arm64`
3. **Configure Handler & Resources**:
   - Under **Runtime settings**, set Handler to: `lambda_handler.handler`
   - Under **Configuration → General configuration**:
     - **Memory**: `512 MB` (or `1024 MB`)
     - **Timeout**: `30 seconds` (to comfortably accommodate Bedrock model inference)
4. **Set Environment Variables**:
   Under **Configuration → Environment variables**, add:
   - `AWS_REGION` = `us-east-1`
   - `BEDROCK_MODEL_ID` = `us.amazon.nova-2-lite-v1:0`
   - `ALLOWED_ORIGINS` = `*` (or your future Amplify domain, e.g. `https://main.d123456.amplifyapp.com`)

---

### STEP 2: Configure Lambda IAM Role Permissions

1. In the Lambda function page, go to **Configuration → Permissions**.
2. Click the **Execution Role name** to open IAM Console.
3. Click **Add permissions → Attach policies** (or **Create inline policy**):
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Action": [
           "bedrock:InvokeModel",
           "bedrock:InvokeModelWithResponseStream"
         ],
         "Resource": [
           "arn:aws:bedrock:us-east-1:*:inference-profile/us.amazon.nova-2-lite-v1:0",
           "arn:aws:bedrock:us-east-1::foundation-model/*"
         ]
       }
     ]
   }
   ```
4. Save the policy. (No access keys needed; Lambda assumes this role automatically).

---

### STEP 3: Create Amazon API Gateway HTTP API

1. **Open AWS Console → API Gateway**:
   - Click **Create API** → Under **HTTP API**, click **Build**.
2. **Configure Integration**:
   - **Integration type**: `Lambda`
   - **Lambda function**: `joblens-ai-backend`
   - **API name**: `joblens-ai-api`
3. **Configure Routes**:
   - Method: `ANY`
   - Resource path: `/{proxy+}`
   - Integration: `joblens-ai-backend`
4. **Configure CORS**:
   - Under API Gateway **CORS**:
     - Access-Control-Allow-Origins: `*`
     - Access-Control-Allow-Methods: `GET, POST, OPTIONS`
     - Access-Control-Allow-Headers: `*`
5. **Copy the Invoke URL**:
   - Example: `https://a1b2c3d4e5.execute-api.us-east-1.amazonaws.com`

---

### STEP 4: Deploy Frontend to AWS Amplify

1. **Push your code to GitHub**.
2. **Open AWS Console → AWS Amplify**:
   - Click **Create new app** → Choose **Host web app**.
   - Select **GitHub** and authorize access to your `JobLensAI` repository.
   - Select the repository and `main` branch.
3. **Build Settings**:
   - Amplify will automatically detect the root `amplify.yml` file:
     - `baseDirectory: frontend/dist`
4. **Configure Environment Variables**:
   - Under **Advanced settings → Environment variables**, add:
     - `VITE_API_BASE_URL` = `https://<YOUR_API_GATEWAY_ID>.execute-api.us-east-1.amazonaws.com`
5. **Deploy**:
   - Click **Save and deploy**.
   - Amplify will automatically run `npm ci`, build the React SPA, and provision an SSL-secured custom URL (e.g. `https://main.d123456.amplifyapp.com`).

---

## 🔒 Security Best Practices Verified

1. **No Hardcoded Keys**: The application uses IAM roles for Bedrock authentication.
2. **In-Memory Document Handling**: Uploaded PDFs are parsed in memory using `pypdf` and never written to permanent disk storage.
3. **Strict Validation**: 10MB file limit and input length checks on both frontend and backend.
4. **Git Protection**: All `.env` files and scratch artifacts are ignored in `.gitignore`.
