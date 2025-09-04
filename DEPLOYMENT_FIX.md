# Railway Deployment Fix

## Problem
Railway's Nixpacks couldn't find a start command, causing deployment to fail.

## Solution
I've created multiple configuration files to ensure Railway can properly start your application:

### Files Created/Updated:

1. **`main.py`** - Root-level entry point that Railway can easily find
2. **`nixpacks.toml`** - Explicit Nixpacks configuration
3. **`Procfile`** - Heroku-style process file
4. **`railway.toml`** - Railway-specific configuration
5. **`Dockerfile`** - Docker configuration (alternative)

## Deployment Options

### Option 1: Use Nixpacks (Recommended)
Railway will automatically use `nixpacks.toml` and `main.py`:
- No additional configuration needed
- Automatic Python environment setup
- Uses `python main.py` as start command

### Option 2: Force Docker
If you want to use Docker instead:
1. In Railway dashboard, go to your project settings
2. Set "Build Command" to: `docker build -t app .`
3. Set "Start Command" to: `docker run -p $PORT:5000 app`

## Testing the Fix

1. **Commit and push your changes:**
   ```bash
   git add .
   git commit -m "Fix Railway deployment configuration"
   git push origin main
   ```

2. **Redeploy on Railway:**
   - Go to your Railway project
   - Click "Deploy" or it will auto-deploy from GitHub

3. **Check the logs:**
   - Railway should now find the start command
   - Look for "Starting with Flask dev server" or "Starting with Gunicorn"

## Expected Behavior

- **Development**: Uses Flask dev server
- **Production**: Uses Gunicorn with multiple workers
- **Health Check**: Available at `/api/health/`
- **Swagger UI**: Available at `/docs/`

## Troubleshooting

If deployment still fails:

1. **Check Railway logs** for specific error messages
2. **Verify environment variables** are set correctly
3. **Try the Docker option** if Nixpacks continues to fail
4. **Contact Railway support** if issues persist

## Environment Variables

Make sure these are set in Railway:
- `FLASK_ENV=production`
- `PORT` (automatically set by Railway)
