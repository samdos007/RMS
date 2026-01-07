# Railway Deployment Guide - RMS Application

## Prerequisites

1. **Railway Account**: Sign up at https://railway.app (free to start)
2. **GitHub Account**: Your code must be in a GitHub repository
3. **Git**: Code pushed to GitHub

---

## Step 1: Prepare Your Code

### 1.1 Ensure all deployment files are present:

✓ `Dockerfile` in root directory
✓ `.dockerignore` in root directory
✓ Updated `backend/app/main.py` with static file serving
✓ Updated `backend/app/config.py` with Railway support

### 1.2 Push to GitHub:

```bash
cd RMS
git add .
git commit -m "Add Railway deployment configuration"
git push origin main
```

---

## Step 2: Create Railway Project

### 2.1 Create New Project

1. Go to https://railway.app/dashboard
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Authorize Railway to access your GitHub account
5. Select your **RMS repository**
6. Railway will automatically detect the Dockerfile and start building

### 2.2 Wait for Initial Build

- Railway will build your Docker image (this takes 2-5 minutes)
- The build may fail initially due to missing environment variables - that's expected!

---

## Step 3: Configure Environment Variables

### 3.1 Open Service Settings

1. Click on your service in Railway dashboard
2. Go to **"Variables"** tab
3. Click **"+ New Variable"**

### 3.2 Add Required Variables

Add these environment variables one by one:

| Variable | Value | Description |
|----------|-------|-------------|
| `SECRET_KEY` | Generate random string | Use: `openssl rand -hex 32` or similar |
| `DEBUG` | `false` | Disable debug mode in production |
| `COOKIE_SECURE` | `true` | Enable secure cookies (HTTPS only) |
| `DATA_DIR` | `/app/data` | Path to data directory |
| `CORS_ORIGINS` | See below | Your Railway domain |

**For CORS_ORIGINS**:
- First, get your Railway public domain from **Settings** → **Networking** → **Public Networking**
- It will look like: `your-app-name.up.railway.app`
- Set CORS_ORIGINS to: `https://your-app-name.up.railway.app`

**To generate SECRET_KEY**:
```bash
# On Mac/Linux:
openssl rand -hex 32

# On Windows (PowerShell):
-join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | % {[char]$_})

# Or use online: https://www.random.org/strings/
```

### 3.3 Apply Variables

- After adding all variables, Railway will automatically redeploy
- Wait for deployment to complete (~2-3 minutes)

---

## Step 4: Add Persistent Storage (Volume)

### 4.1 Create Volume

1. In your service, click **"Settings"**
2. Scroll to **"Volumes"**
3. Click **"+ New Volume"**
4. Configure:
   - **Mount Path**: `/app/data`
   - **Name**: `rms-data` (or any name you prefer)
5. Click **"Add"**

### 4.2 Redeploy

- Railway will automatically redeploy with the volume attached
- This volume will persist your SQLite database and uploaded files

---

## Step 5: Run Database Migrations

The Dockerfile already includes migration command, but you can verify:

### 5.1 Check Logs

1. Go to **"Deployments"** tab
2. Click on the latest deployment
3. Check logs for: `alembic upgrade head`
4. Should see: `Running upgrade  -> 001_initial, -> 002_earnings_guidance, -> 003_add_theme_type, -> ff8c8b068c7d`

### 5.2 Manual Migration (if needed)

If migrations didn't run:
1. Click on your service
2. Go to **"Settings"** → **"Service"**
3. Under "Deploy Command", ensure it's set to:
```bash
alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
```

---

## Step 6: Access Your Application

### 6.1 Get Public URL

1. Go to **"Settings"** → **"Networking"**
2. Under **"Public Networking"**, you'll see your public URL
3. Click to open: `https://your-app-name.up.railway.app`

### 6.2 Initial Setup

1. Open the application URL in your browser
2. You'll see the login/setup page
3. Create your admin password
4. Start using the app!

---

## Step 7: Configure Custom Domain (Optional)

### 7.1 Add Custom Domain

1. Go to **"Settings"** → **"Networking"**
2. Click **"+ Custom Domain"**
3. Enter your domain (e.g., `rms.yourdomain.com`)
4. Follow DNS instructions to add CNAME record

### 7.2 Update CORS

After adding custom domain:
1. Go to **"Variables"**
2. Update `CORS_ORIGINS` to include both Railway and custom domains:
```
https://your-app-name.up.railway.app,https://rms.yourdomain.com
```

---

## Monitoring & Maintenance

### Check Logs

- **Deployments** tab → Click deployment → View real-time logs
- Useful for debugging errors

### Resource Usage

- **Metrics** tab shows CPU, RAM, and network usage
- Railway Hobby plan includes: $5/month credit, 500 MB RAM, shared CPU

### Database Backups

⚠️ **Important**: Railway volumes are persistent but:
1. Go to your service **Settings** → **Volumes**
2. Click on your volume → **"Create Snapshot"** (manual backup)
3. Set up periodic backups or download SQLite file via shell

### Download Database (for local backup):

1. Go to service → **Settings** → **Service**
2. Open **"Command Palette"** or use Railway CLI
3. Run:
```bash
railway run cat /app/data/rms.db > backup.db
```

---

## Troubleshooting

### App won't start

**Check**:
1. Logs show database migration errors?
   - Volume might not be mounted - check Settings → Volumes
2. "Address already in use"?
   - Railway auto-assigns PORT - don't hardcode port
3. Secret key error?
   - Ensure SECRET_KEY is set and at least 32 characters

### Can't login

**Check**:
1. CORS errors in browser console?
   - Update CORS_ORIGINS to match your Railway domain exactly
2. Cookies not working?
   - Ensure COOKIE_SECURE=true and using HTTPS

### Files/data disappearing

**Check**:
1. Volume mounted correctly?
   - Settings → Volumes → Mount path should be `/app/data`
2. Database in the right location?
   - Logs should show: `Using database: /app/data/rms.db`

### Frontend not loading

**Check**:
1. Frontend build succeeded?
   - Check build logs for `npm run build` success
2. Static files copied?
   - Logs should show static directory exists
3. Routes not working?
   - Ensure frontend serving code is in main.py

---

## Costs

**Railway Hobby Plan**: $5/month
- Includes $5 usage credit
- Shared CPU, 512MB RAM
- Perfect for personal/small team use

**Usage estimate for RMS**:
- Single service: ~$5/month
- Volume storage (1-2GB): Included
- Bandwidth: Included for reasonable use

**Upgrade** if you need:
- More resources
- Multiple environments (staging/prod)
- Team features

---

## Next Steps

1. ✅ Deploy application
2. ✅ Set up periodic database backups
3. ✅ Configure custom domain (optional)
4. 📊 Monitor usage and performance
5. 🔐 Keep SECRET_KEY secure (rotate if compromised)

---

## Support

- **Railway Docs**: https://docs.railway.app
- **Railway Discord**: https://discord.gg/railway
- **Status Page**: https://status.railway.app

---

## Migrating to PostgreSQL (Future)

If you outgrow SQLite, Railway makes PostgreSQL easy:

1. Railway Dashboard → **"+ New"** → **"Database"** → **"PostgreSQL"**
2. Railway auto-generates DATABASE_URL
3. Add to your service variables
4. Redeploy - app auto-switches to PostgreSQL
5. Run migrations: `alembic upgrade head`

SQLite → PostgreSQL migration requires data export/import but structure is compatible.
