# 🚂 Step-by-Step Railway Deployment Guide

This guide walks you through deploying your **Distributed Rate Limiter API Gateway & Microservice Architecture** on [Railway.app](https://railway.app).

---

## 🏗️ Architecture on Railway

On Railway, your project will consist of **4 Services** running in a single Railway Project:

1. **Redis Database**: Managed Redis service provided by Railway.
2. **User Service**: Standalone FastAPI app deployed from `services/user_service/Dockerfile`.
3. **Product Service**: Standalone FastAPI app deployed from `services/product_service/Dockerfile`.
4. **API Gateway**: Main API Gateway app deployed from root `Dockerfile`.

---

## 🚀 Deployment Steps (GitHub Integration Method)

### Step 1: Push Project to GitHub
Ensure all latest changes are committed and pushed to your GitHub repository:

```bash
git add .
git commit -m "Configure project for Railway deployment"
git push origin main
```

---

### Step 2: Create a New Project on Railway
1. Go to [railway.app](https://railway.app) and sign in.
2. Click **"New Project"**.
3. Select **"Deploy from GitHub repo"** and choose your repository.

---

### Step 3: Add Managed Redis Database
1. Inside your Railway project dashboard, click **"+ New"** button.
2. Select **"Database"** ──▶ **"Add Redis"**.
3. Railway will provision a Redis instance.
4. Click on the Redis service box, go to the **"Variables"** tab, and copy `REDIS_URL` or `REDIS_PRIVATE_URL`.

---

### Step 4: Deploy Downstream Microservices

#### 4A. Deploy User Service
1. Click **"+ New"** ──▶ **"GitHub Repo"** ──▶ Select your repository.
2. Rename this service to `user-service`.
3. Go to **Settings** ──▶ **Build**:
   - Set **Dockerfile Path** to: `services/user_service/Dockerfile`
4. Go to **Networking**:
   - Click **"Generate Domain"** (e.g. `user-service-production.up.railway.app`).
   - Copy the private or public domain URL (e.g. `https://user-service-production.up.railway.app`).

#### 4B. Deploy Product Service
1. Click **"+ New"** ──▶ **"GitHub Repo"** ──▶ Select your repository.
2. Rename this service to `product-service`.
3. Go to **Settings** ──▶ **Build**:
   - Set **Dockerfile Path** to: `services/product_service/Dockerfile`
4. Go to **Networking**:
   - Click **"Generate Domain"** (e.g. `product-service-production.up.railway.app`).
   - Copy the domain URL.

---

### Step 5: Deploy API Gateway Service
1. Click **"+ New"** ──▶ **"GitHub Repo"** ──▶ Select your repository.
2. Rename this service to `api-gateway`.
3. Go to **Settings** ──▶ **Build**:
   - Set **Dockerfile Path** to: `Dockerfile`
4. Go to **Variables** tab and add the following Environment Variables:

| Variable Name | Value / Description | Example Value |
| :--- | :--- | :--- |
| `REDIS_URL` | Select **Reference Variable** ──▶ `${{Redis.REDIS_URL}}` | Auto-linked |
| `USER_SERVICE_URL` | URL of deployed User Service | `https://user-service-production.up.railway.app` |
| `PRODUCT_SERVICE_URL` | URL of deployed Product Service | `https://product-service-production.up.railway.app` |
| `JWT_SECRET_KEY` | Your secure JWT key | `super_secret_jwt_key_999` |
| `ADMIN_KEY` | Your admin secret key | `admin-secret-key-12345` |
| `DEBUG` | `False` | `False` |

5. Go to **Networking**:
   - Click **"Generate Domain"** for `api-gateway` (e.g. `api-gateway-production.up.railway.app`).

---

## 🧪 Verifying Deployment

Once Railway completes building all services, test your live production API Gateway:

### 1. Gateway Health Check
```bash
curl https://api-gateway-production.up.railway.app/health
```
**Expected Response**:
```json
{
  "success": true,
  "service": "Distributed Rate Limiter Gateway",
  "status": "healthy",
  "version": "1.0.0"
}
```

### 2. Swagger Documentation UI
Open browser at: `https://api-gateway-production.up.railway.app/docs`

### 3. Generate API Key via Admin Route
```bash
curl -X POST "https://api-gateway-production.up.railway.app/admin/api-key/my_client" \
  -H "X-Admin-Key: admin-secret-key-12345"
```

### 4. Call Proxied User Microservice with API Key & JWT
```bash
curl -X GET "https://api-gateway-production.up.railway.app/users" \
  -H "X-API-Key: <YOUR_GENERATED_API_KEY>" \
  -H "Authorization: Bearer <YOUR_JWT_TOKEN>"
```

---

## 🛠️ Alternative: Deploying via Railway CLI

If you prefer using the command line:

```bash
# 1. Install Railway CLI
npm i -g @railway/cli

# 2. Login to Railway
railway login

# 3. Link or create project
railway link

# 4. Deploy gateway service
railway up
```
