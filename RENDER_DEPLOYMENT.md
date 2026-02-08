# 🚀 Render Deployment Guide - Claude Opus 4.5

> Deploy your AI API to production in **5 minutes** - **Completely FREE!**

---

## 📋 Table of Contents

1. [Quick Deploy (Recommended)](#quick-deploy-recommended)
2. [Manual Deploy](#manual-deploy)
3. [Configuration](#configuration)
4. [Testing Deployment](#testing-deployment)
5. [Troubleshooting](#troubleshooting)
6. [Custom Domain](#custom-domain)
7. [Monitoring](#monitoring)

---

## ⚡ Quick Deploy (Recommended)

### Step 1: Push to GitHub ✅

Aapka code already GitHub pe hai, so this step done!

```bash
# Verify latest changes
git status
git add .
git commit -m "Ready for deployment"
git push origin main
```

### Step 2: Connect to Render 🔗

1. **Visit Render:** [https://dashboard.render.com/](https://dashboard.render.com/)

2. **Sign Up/Login:**
   - Click "Get Started for Free"
   - Sign up with GitHub account (easiest)
   - Authorize Render to access repositories

3. **Create New Web Service:**
   - Click **"New +"** button (top right)
   - Select **"Web Service"**

### Step 3: Configure Service ⚙️

#### **Connect Repository:**
```
1. Search for: claude-opus-chatbot
2. Click "Connect" next to your repository
3. If not visible, click "Configure account" and grant access
```

#### **Basic Settings:**
```yaml
Name: claude-opus-enhanced
  (या कोई भी unique name)

Region: Singapore
  (भारत के लिए best - low latency)

Branch: main
  (default branch)

Root Directory: .
  (leave blank या . enter करें)
```

#### **Build Settings:**
```yaml
Runtime: Python 3

Build Command:
pip install --upgrade pip && pip install -r requirements.txt

Start Command:
uvicorn claude_opus_enhanced:app --host 0.0.0.0 --port $PORT --workers 1
```

#### **Plan:**
```
Select: Free
✅ 512 MB RAM
✅ Shared CPU
✅ 750 hours/month (enough for 24/7)
✅ Auto-sleep after 15 min inactivity
```

### Step 4: Deploy! 🎉

1. Click **"Create Web Service"** button
2. Render will automatically:
   - Clone your repository
   - Install dependencies
   - Start your application
   - Assign a URL

**Deployment Time:** 3-5 minutes ⏱️

### Step 5: Get Your URL 🌐

After deployment:
```
Your API URL:
https://claude-opus-enhanced.onrender.com

API Docs:
https://claude-opus-enhanced.onrender.com/docs

Health Check:
https://claude-opus-enhanced.onrender.com/health
```

---

## 🛠️ Manual Deploy

### Option A: Using Render.yaml (Auto-Config)

**Your repo already has `render.yaml`, so:**

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +" → "Blueprint"**
3. Connect repository: `Aman262626/claude-opus-chatbot`
4. Render reads `render.yaml` and auto-configures
5. Click **"Apply"**
6. Done! 🎉

### Option B: Manual Configuration

If render.yaml doesn't work:

```bash
# Step 1: Create Procfile (optional)
echo "web: uvicorn claude_opus_enhanced:app --host 0.0.0.0 --port \$PORT" > Procfile

# Step 2: Ensure runtime.txt exists
echo "python-3.10.0" > runtime.txt

# Step 3: Push changes
git add .
git commit -m "Add deployment files"
git push origin main
```

Then follow Quick Deploy steps.

---

## ⚙️ Configuration

### Environment Variables (Optional)

Render Dashboard → Your Service → Environment:

```bash
# Optional (for future enhancements)
GEMINI_API_KEY=your_gemini_api_key_here
OPENWEATHER_API_KEY=your_weather_key
LOG_LEVEL=info
```

**Add करने के लिए:**
1. Service के "Environment" tab में जाएं
2. "Add Environment Variable" click करें
3. Key और Value enter करें
4. Save करें

### Custom Start Command

Different workers के लिए:

```bash
# Single worker (recommended for free tier)
uvicorn claude_opus_enhanced:app --host 0.0.0.0 --port $PORT --workers 1

# Multiple workers (paid plans)
uvicorn claude_opus_enhanced:app --host 0.0.0.0 --port $PORT --workers 4

# With auto-reload (development only)
uvicorn claude_opus_enhanced:app --host 0.0.0.0 --port $PORT --reload
```

---

## 🧪 Testing Deployment

### Test 1: Health Check

```bash
curl https://your-app.onrender.com/health

# Expected Response:
{
  "status": "optimal",
  "model": "claude-opus-4.5-enhanced",
  ...
}
```

### Test 2: API Docs

Browser में खोलें:
```
https://your-app.onrender.com/docs
```

Interactive API documentation देखेंगे!

### Test 3: Chat Endpoint

```python
import requests

API = "https://your-app.onrender.com"

response = requests.post(f"{API}/chat", json={
    "message": "Hello! Are you working?",
    "user_id": "test_user"
})

print(response.json())
```

### Test 4: Deep Reasoning

```bash
curl -X POST https://your-app.onrender.com/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Calculate 25% of 10000",
    "enable_tools": true
  }'
```

---

## 🐛 Troubleshooting

### Issue 1: Build Failed

**Error:** `requirements.txt not found`

**Solution:**
```bash
# Ensure requirements.txt exists
ls requirements.txt

# If missing, create it
pip freeze > requirements.txt
git add requirements.txt
git commit -m "Add requirements"
git push
```

### Issue 2: Application Timeout

**Error:** `Service failed to bind to port`

**Solution:**
Check start command uses `$PORT`:
```bash
uvicorn claude_opus_enhanced:app --host 0.0.0.0 --port $PORT
```

### Issue 3: Import Errors

**Error:** `Module not found`

**Solution:**
```bash
# Add missing packages to requirements.txt
echo "package-name==version" >> requirements.txt
git add requirements.txt
git commit -m "Fix dependencies"
git push

# Render will auto-redeploy
```

### Issue 4: Slow First Response

**Reason:** Free tier services sleep after 15 min inactivity

**Solutions:**

**Option A: Keep-Alive Ping (Free)**
```python
# Use cron-job.org or UptimeRobot
# Ping every 10 minutes:
GET https://your-app.onrender.com/health
```

**Option B: Upgrade to Paid Plan**
- $7/month - No sleep
- Always-on service

### Issue 5: 512 MB Memory Limit

**Error:** `Out of memory`

**Solutions:**
1. Reduce context window size in code
2. Optimize memory usage
3. Upgrade to paid plan (more RAM)

---

## 🌐 Custom Domain

### Free Subdomain (Automatic)

```
Default: https://claude-opus-enhanced.onrender.com
```

### Custom Domain (Optional)

1. **Buy Domain** (Namecheap, GoDaddy, etc.)

2. **Add to Render:**
   - Service → Settings → Custom Domains
   - Enter your domain
   - Get CNAME record

3. **Update DNS:**
   ```
   Type: CNAME
   Name: api (or @)
   Value: claude-opus-enhanced.onrender.com
   ```

4. **Wait for SSL:**
   - Render automatically provides free SSL
   - 5-10 minutes

5. **Access:**
   ```
   https://api.yourdomain.com
   ```

---

## 📊 Monitoring

### Render Dashboard

**Real-time Metrics:**
```
Service → Metrics tab

✅ CPU Usage
✅ Memory Usage
✅ Request Count
✅ Response Time
✅ Error Rate
```

### Logs

```
Service → Logs tab

Real-time logs:
- Application output
- Errors
- Requests
- Build logs
```

### Health Check Setup

```
Service → Settings → Health Check Path

Path: /health

Render automatically pings:
- Every 30 seconds
- Restarts if unhealthy
```

---

## 🚀 Post-Deployment

### 1. Test All Endpoints

```python
import requests

API = "https://your-app.onrender.com"

# Test chat
requests.post(f"{API}/chat", json={...})

# Test vision
requests.post(f"{API}/vision", json={...})

# Test deep reasoning
requests.post(f"{API}/deep-reasoning", json={...})
```

### 2. Share Your API

```
API Base URL:
https://your-app.onrender.com

API Documentation:
https://your-app.onrender.com/docs

Health Check:
https://your-app.onrender.com/health
```

### 3. Integrate with Apps

Telegram Bot, Web App, Mobile App में integrate करें:

```python
# Python
API_BASE = "https://your-app.onrender.com"

# JavaScript
const API_BASE = 'https://your-app.onrender.com';

# cURL
curl https://your-app.onrender.com/chat
```

---

## 🔄 Auto-Deploy

**Already configured!** ✅

```yaml
# render.yaml has:
autoDeploy: true
```

Means:
```bash
# Har GitHub push pe auto-deploy
git add .
git commit -m "Update features"
git push origin main

# Render automatically:
# 1. Detects push
# 2. Rebuilds
# 3. Redeploys
# 4. Live in 3-5 minutes
```

---

## 💰 Cost Breakdown

### Free Tier (Current)
```
✅ FREE forever
✅ 512 MB RAM
✅ Shared CPU
✅ 750 hours/month
✅ Auto-sleep after 15 min
✅ Free SSL
✅ Automatic deploys
```

### Paid Plans (Optional)

**Starter: $7/month**
```
✅ No sleep
✅ 512 MB RAM
✅ Always available
```

**Standard: $25/month**
```
✅ 2 GB RAM
✅ More CPU
✅ Better performance
```

---

## 📱 Keep Service Awake (Free Tier)

### Method 1: UptimeRobot (Recommended)

1. Visit [UptimeRobot.com](https://uptimerobot.com/)
2. Sign up (free)
3. Add New Monitor:
   ```
   Monitor Type: HTTP(s)
   Friendly Name: Claude Opus API
   URL: https://your-app.onrender.com/health
   Monitoring Interval: 5 minutes
   ```
4. Save

**Result:** API stays awake 24/7! 🎉

### Method 2: Cron-job.org

1. Visit [cron-job.org](https://cron-job.org/)
2. Create account
3. Create cronjob:
   ```
   URL: https://your-app.onrender.com/health
   Schedule: */10 * * * * (every 10 min)
   ```

### Method 3: Custom Script

```python
# keep_alive.py
import requests
import time

API = "https://your-app.onrender.com/health"

while True:
    try:
        requests.get(API)
        print("✅ Pinged")
    except:
        print("❌ Failed")
    time.sleep(600)  # 10 minutes
```

Run on:
- Your computer (if always on)
- Another free service
- Replit, PythonAnywhere

---

## 🔐 Security

### 1. Environment Variables

Never commit sensitive data:
```bash
# .gitignore (already exists)
.env
*.key
secrets.json
```

### 2. HTTPS

Render provides free SSL automatically ✅

### 3. Rate Limiting (Future)

Add in code:
```python
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/chat")
@limiter.limit("20/minute")
async def chat(...):
    ...
```

---

## 📝 Checklist

### Pre-Deployment
- [x] Code pushed to GitHub
- [x] `requirements.txt` exists
- [x] `render.yaml` configured
- [x] `runtime.txt` has Python version
- [x] Start command correct

### During Deployment
- [ ] Render account created
- [ ] Repository connected
- [ ] Service configured
- [ ] Build successful
- [ ] Service running

### Post-Deployment
- [ ] Health check working
- [ ] API docs accessible
- [ ] Test endpoints successful
- [ ] UptimeRobot setup (optional)
- [ ] Custom domain added (optional)

---

## 🎉 Success!

Aapka Claude Opus 4.5 Enhanced ab **live on production**! 🚀

**Your URLs:**
```
API: https://your-app.onrender.com
Docs: https://your-app.onrender.com/docs
Health: https://your-app.onrender.com/health
```

**Next Steps:**
1. Test all endpoints
2. Share API with team
3. Integrate with your apps
4. Setup UptimeRobot
5. Monitor performance

---

## 🆘 Need Help?

- **Render Docs:** [https://render.com/docs](https://render.com/docs)
- **GitHub Issues:** [Report problems](https://github.com/Aman262626/claude-opus-chatbot/issues)
- **Render Support:** support@render.com

---

**Deployment Guide by Aman262626** ❤️

**Last Updated:** February 2026
