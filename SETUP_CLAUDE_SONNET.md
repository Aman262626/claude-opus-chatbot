# 🌟 Claude 3.5 Sonnet API Setup Guide

## 🛠️ Prerequisites

- GitHub account (you have it ✅)
- Render account (you have it ✅)
- Anthropic Claude API key (need to create)

---

## Step 1: Get Claude API Key 🔐

### Register at Anthropic

1. Visit: **https://console.anthropic.com/**
2. Sign up with Google / Email
3. Verify your email
4. Go to **API Keys** section
5. Click **Create Key**
6. Copy the key (starts with `sk-ant-...`)
7. **SAVE IT SECURELY!**

### Free Tier
```
- $5 free credits
- Enough for ~10,000 requests
- After that: Pay per token
```

---

## Step 2: Add Environment Variable to Render ✅

### Method A: Via Render Dashboard

1. **Go to Render:** https://dashboard.render.com
2. **Click** your service (`claude-opus-chatbot`)
3. **Click** `Settings` tab
4. **Scroll** to "Environment"
5. **Click** `Add Environment Variable`
6. **Enter:**
   ```
   Name:  CLAUDE_API_KEY
   Value: sk-ant-xxxxx... (paste your key)
   ```
7. **Click** `Save`

### Method B: Via Environment File

Create `.env` file locally:
```bash
echo "CLAUDE_API_KEY=sk-ant-xxxxx" > .env
```

**Never commit this file!**
```bash
echo ".env" >> .gitignore
```

---

## Step 3: Update Repository 🛠️

### Option 1: Switch to Claude Sonnet (Replace Opus)

Update `Procfile`:
```bash
# Change from:
web: gunicorn app:app

# To:
web: gunicorn claude_sonnet_api:app
```

### Option 2: Keep Both APIs (Advanced)

Create `app_selector.py`:
```python
import os
from flask import Flask, request, jsonify

# Choose based on environment variable
if os.environ.get('USE_CLAUDE'):
    from claude_sonnet_api import app as selected_app
else:
    from app import app as selected_app

app = selected_app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
```

Then in `Procfile`:
```bash
web: gunicorn app_selector:app
```

Switch with environment variable:
```bash
# Use Claude
heroku config:set USE_CLAUDE=true

# Use Opus
heroku config:unset USE_CLAUDE
```

---

## Step 4: Deploy 🚀

### Push to Render

```bash
# Make changes
git add .
git commit -m "Add Claude 3.5 Sonnet API"
git push origin main
```

### Render Auto-Deploy

Render will:
1. Detect new changes
2. Re-build (30-60 seconds)
3. Deploy with new `Procfile`
4. Restart service

### Verify Deployment

```bash
# Check health
curl https://claude-opus-chatbot.onrender.com/health

# Should show:
{
  "model": "claude-3-5-sonnet-20241022",
  "features_active": {
    "claude_api": true
  }
}
```

---

## Step 5: Test Claude API 🤖

### Test 1: Simple Chat

```bash
curl -X POST https://claude-opus-chatbot.onrender.com/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello Claude! What is 2+2?",
    "user_id": "test123"
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "response": "2 + 2 = 4...",
  "model_used": "claude-3-5-sonnet",
  "type": "text"
}
```

### Test 2: Hinglish Chat

```bash
curl -X POST https://claude-opus-chatbot.onrender.com/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Bhai Python mein loop kaise likhte hain?",
    "user_id": "test123"
  }'
```

### Test 3: Image Generation

```bash
curl -X POST https://claude-opus-chatbot.onrender.com/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Generate image of a beautiful sunset",
    "user_id": "test123"
  }'
```

---

## 💰 Pricing & Cost Management

### Claude 3.5 Sonnet Pricing

```
Input:  $3.00 per 1M tokens
Output: $15.00 per 1M tokens

Example costs:
- 100 messages (500 tokens avg) = $0.15
- 1,000 messages = $1.50
- 10,000 messages = $15
```

### Free Credits

```
- New account: $5 free
- Usually 2-3 months of testing
- After that: Pay per usage
```

### Cost Optimization

1. **Monitor usage:**
   ```
   Anthropic Console → Usage
   ```

2. **Set spending limit:**
   ```
   Console → Settings → Spending Limit
   ```

3. **Use Opus fallback:**
   - Claude fails → Automatically uses Opus (free)
   - No service interruption

---

## 🔧 Troubleshooting

### Issue: API key not found

```
Error: "CLAUDE_API_KEY environment variable not set"

Fix:
1. Check Render Settings → Environment
2. Verify key is saved
3. Restart service
```

### Issue: Invalid API key

```
Error: "Invalid API key"

Fix:
1. Check key starts with "sk-ant-"
2. Paste full key (no truncation)
3. No extra spaces
```

### Issue: Authentication failed

```
Error: "Authentication failed"

Fix:
1. Regenerate key in Anthropic Console
2. Update environment variable
3. Restart Render service
```

### Issue: Rate limited

```
Error: "Rate limit exceeded"

Fix:
1. Reduce request frequency
2. Add delays between requests
3. Check Anthropic dashboard for limits
```

---

## 🔍 Monitoring

### Check API Usage

**Anthropic Console:**
```
https://console.anthropic.com/ → Usage
```

**Render Logs:**
```
Render Dashboard → Service → Logs
Search for: "claude-3-5-sonnet"
```

### Alerts & Notifications

```
1. Render → Settings → Notifications
2. Alert on deployment failure
3. Alert on high error rate
```

---

## 🚀 Advanced Features

### 1. Fallback to Opus

Automatic fallback if Claude fails:
```python
def get_claude_response(...):
    try:
        # Try Claude
        return claude_response
    except:
        # Fallback to Opus
        return get_fallback_response(...)
```

### 2. Multi-Model Selection

```bash
# Request specific model
{
  "message": "...",
  "user_id": "...",
  "model": "claude"  # or "opus"
}
```

### 3. Streaming Responses

```python
# For large responses
def stream_response():
    for chunk in claude.stream(message):
        yield chunk
```

---

## 🛦️ Rollback

If Claude API has issues, revert to Opus:

```bash
# Update Procfile
web: gunicorn app:app

# Push
git push origin main

# Render auto-redeploys
```

---

## 📺 Real-Time Monitoring

### Command to watch logs:
```bash
# Render (need to install CLI)
render logs --service claude-opus-chatbot --tail

# Or via dashboard
https://dashboard.render.com → Logs tab
```

---

## ✅ Verification Checklist

- [ ] Anthropic account created
- [ ] API key generated
- [ ] Environment variable added to Render
- [ ] claude_sonnet_api.py in repository
- [ ] Procfile updated (or app_selector.py setup)
- [ ] Changes pushed to GitHub
- [ ] Render deployment completed
- [ ] /health endpoint returns claude model
- [ ] Test message works
- [ ] Hinglish message works
- [ ] Image generation works

---

## 📞 Support

**Anthropic Docs:** https://docs.anthropic.com/
**API Reference:** https://docs.anthropic.com/en/api/getting-started
**Status:** https://status.anthropic.com/

---

**Setup complete!** Your API is now using Claude 3.5 Sonnet 🌟
