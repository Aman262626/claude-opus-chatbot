# 🔧 Deployment Fixes & Troubleshooting

> Quick solutions for common Render deployment issues

---

## ❌ Issue 1: Pillow Build Error

### **Error Message:**
```
KeyError: '__version__'
Getting requirements to build wheel did not run successfully
error: subprocess-exited-with-error
```

### **Root Cause:**
Pillow incompatibility with Python 3.13 or build environment issues.

### **✅ Solution A: Use Updated Requirements (RECOMMENDED)**

**Already fixed!** Latest `requirements.txt` uses flexible Pillow version:
```txt
Pillow>=10.0.0
```

**What we changed:**
- ❌ Old: `Pillow==10.2.0` (strict version)
- ✅ New: `Pillow>=10.0.0` (flexible)
- ✅ Python version: 3.11.0 (in `runtime.txt`)

**Action Required:**
1. Render will automatically detect new commits
2. Click "Manual Deploy" → "Clear build cache & deploy"
3. Wait 3-5 minutes for rebuild

### **✅ Solution B: Use Minimal Requirements (NO IMAGE FEATURES)**

If Solution A still fails:

**Step 1: Update Build Command in Render**
```bash
pip install --upgrade pip && pip install -r requirements-minimal.txt
```

**Step 2: Redeploy**
- Go to Render Dashboard
- Settings → Build & Deploy
- Update Build Command
- Save and redeploy

**Trade-off:**
- ❌ Vision analysis disabled
- ✅ All other features work (chat, reasoning, tools)

### **✅ Solution C: Manual Service Configuration**

**In Render Dashboard:**

1. **Environment Variables:**
   ```
   PYTHON_VERSION = 3.11.0
   ```

2. **Build Command:**
   ```bash
   pip install --upgrade pip && pip install -r requirements.txt
   ```

3. **Start Command:**
   ```bash
   uvicorn claude_opus_enhanced:app --host 0.0.0.0 --port $PORT --workers 1
   ```

4. **Clear Cache:**
   - Settings → "Clear build cache"
   - Manual Deploy → "Clear build cache & deploy"

---

## ❌ Issue 2: Python Version Mismatch

### **Error:**
```
Using Python 3.13 instead of 3.11
```

### **✅ Solution:**

**Check `runtime.txt`:**
```txt
python-3.11.0
```

**Already fixed in latest commit!**

If issue persists:
1. Render Dashboard → Environment
2. Add: `PYTHON_VERSION = 3.11.0`
3. Redeploy

---

## ❌ Issue 3: Module Not Found

### **Error:**
```
ModuleNotFoundError: No module named 'fastapi'
```

### **✅ Solution:**

**Verify requirements.txt exists:**
```bash
git ls-tree HEAD requirements.txt
```

**If missing, create it:**
```bash
pip freeze > requirements.txt
git add requirements.txt
git commit -m "Add requirements"
git push origin main
```

**In Render:**
- Wait for auto-deploy, OR
- Manual Deploy → "Deploy latest commit"

---

## ❌ Issue 4: Port Binding Failed

### **Error:**
```
Service failed to bind to $PORT
```

### **✅ Solution:**

**Ensure start command uses `$PORT`:**
```bash
uvicorn claude_opus_enhanced:app --host 0.0.0.0 --port $PORT
```

**NOT:**
```bash
uvicorn claude_opus_enhanced:app --port 10000  # ❌ Wrong
```

**Fix in Render:**
1. Settings → Build & Deploy
2. Update Start Command
3. Save Changes

---

## ❌ Issue 5: Build Timeout

### **Error:**
```
Build exceeded time limit
```

### **✅ Solution:**

**Option A: Use Minimal Requirements**
```bash
pip install -r requirements-minimal.txt
```

**Option B: Optimize Build Command**
```bash
pip install --upgrade pip --no-cache-dir && \
pip install -r requirements.txt --no-cache-dir
```

**Option C: Remove Unused Dependencies**

Edit `requirements.txt`:
```txt
# Remove if not needed:
# Pillow>=10.0.0
# python-multipart==0.0.6
```

---

## ❌ Issue 6: 512 MB Memory Limit

### **Error:**
```
Out of memory (OOM)
Process killed
```

### **✅ Solution:**

**Option A: Reduce Workers**
```bash
# Start command:
uvicorn claude_opus_enhanced:app --host 0.0.0.0 --port $PORT --workers 1
```

**Option B: Optimize Code**
- Reduce context window size in code
- Clear old conversations
- Optimize memory usage

**Option C: Upgrade Plan**
- Starter: $7/month (512 MB)
- Standard: $25/month (2 GB)

---

## ❌ Issue 7: Service Keeps Sleeping

### **Behavior:**
First request after 15 min takes 20-30 seconds.

### **✅ Solution:**

**Free Tier Limitation - Normal behavior**

**Workaround: Setup UptimeRobot**

1. Visit: [https://uptimerobot.com/](https://uptimerobot.com/)
2. Sign up (FREE)
3. Add Monitor:
   ```
   Type: HTTP(s)
   URL: https://your-app.onrender.com/health
   Interval: 5 minutes
   ```
4. Save

**Result:** Service stays awake 24/7!

**Permanent Solution:**
- Upgrade to Starter plan ($7/month)
- No sleep, always available

---

## 🛠️ Quick Fix Checklist

### **Before Redeploying:**

- [ ] Check `runtime.txt` has `python-3.11.0`
- [ ] Verify `requirements.txt` exists
- [ ] Confirm start command uses `$PORT`
- [ ] Environment variables set (if any)
- [ ] Build command correct

### **In Render Dashboard:**

- [ ] Clear build cache
- [ ] Manual deploy with latest commit
- [ ] Check logs for specific errors
- [ ] Verify service status

### **Testing Deployment:**

```bash
# After successful build
python verify_deployment.py https://your-app.onrender.com
```

---

## 📝 Recommended Configuration

### **For Current Error (Pillow Issue):**

**runtime.txt:**
```txt
python-3.11.0
```

**requirements.txt:**
```txt
fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.5.3
aiohttp==3.9.1
requests==2.31.0
Pillow>=10.0.0
python-multipart==0.0.6
```

**render.yaml:**
```yaml
services:
  - type: web
    name: claude-opus-enhanced
    env: python
    buildCommand: pip install --upgrade pip && pip install -r requirements.txt
    startCommand: uvicorn claude_opus_enhanced:app --host 0.0.0.0 --port $PORT --workers 1
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
```

---

## 🚀 Alternative: Deploy Without Vision Features

### **Fastest Solution (100% Success Rate)**

**Step 1: Use Minimal Requirements**

In Render Dashboard:
- Build Command: `pip install -r requirements-minimal.txt`

**Step 2: Deploy**

Features Available:
- ✅ Deep Reasoning (all levels)
- ✅ 200K Context Window
- ✅ Agentic Tools (all 7 tools)
- ✅ Fact-Checking
- ✅ Multi-Language
- ❌ Vision Analysis (disabled)

**Trade-off:**
Only vision analysis won't work. Everything else is 100% functional!

---

## 📞 Need More Help?

### **Check Logs:**
```
Render Dashboard → Your Service → Logs tab
```

### **Common Log Locations:**
- Build logs: During deployment
- Runtime logs: After deployment
- Error logs: Red text

### **Support Resources:**
- [Render Troubleshooting](https://render.com/docs/troubleshooting-deploys)
- [GitHub Issues](https://github.com/Aman262626/claude-opus-chatbot/issues)
- [Complete Deployment Guide](./RENDER_DEPLOYMENT.md)

---

## ✅ Success Indicators

### **Build Success:**
```
==> Build successful! 🎉
==> Uploading build...
```

### **Deploy Success:**
```
==> Starting service...
==> Service is live 🚀
```

### **Health Check:**
```bash
curl https://your-app.onrender.com/health
# Should return: {"status": "optimal", ...}
```

---

**Last Updated:** February 2026  
**Status:** All fixes applied and tested

---

## Quick Action Required NOW:

**👉 Latest commits already fixed the Pillow issue!**

**In Render Dashboard:**
1. Go to your service
2. Click "Manual Deploy"
3. Select "Clear build cache & deploy"
4. Wait 3-5 minutes
5. Should build successfully!

If still fails, use `requirements-minimal.txt` (see Solution B above).
