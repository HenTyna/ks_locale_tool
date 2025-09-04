# Railway Deployment Guide

This guide explains how to deploy the Locale Tool API to Railway.

## Prerequisites

1. **Railway Account**: Sign up at [railway.app](https://railway.app)
2. **GitHub Repository**: Your code should be in a GitHub repository
3. **Railway CLI** (optional): Install with `npm install -g @railway/cli`

## Deployment Steps

### Method 1: Railway Dashboard (Recommended)

1. **Connect Repository**:
   - Go to [railway.app](https://railway.app)
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository

2. **Configure Environment**:
   - Railway will automatically detect the Dockerfile
   - Set environment variables:
     - `FLASK_ENV=production`
     - `PORT` (automatically set by Railway)

3. **Deploy**:
   - Railway will build and deploy automatically
   - Your API will be available at the provided Railway URL

### Method 2: Railway CLI

1. **Login to Railway**:
   ```bash
   railway login
   ```

2. **Initialize Project**:
   ```bash
   railway init
   ```

3. **Set Environment Variables**:
   ```bash
   railway variables set FLASK_ENV=production
   ```

4. **Deploy**:
   ```bash
   railway up
   ```

## Environment Variables

Railway will automatically set:
- `PORT`: The port your app should listen on
- `RAILWAY_STATIC_URL`: Your app's public URL

You can set additional variables in the Railway dashboard:
- `FLASK_ENV=production`: Ensures production mode

## API Endpoints

Once deployed, your API will be available at:
- **Health Check**: `https://your-app.railway.app/api/health/`
- **Search**: `https://your-app.railway.app/api/search/`
- **Apply**: `https://your-app.railway.app/api/apply/`
- **Swagger UI**: `https://your-app.railway.app/docs/`

## Testing Your Deployment

1. **Health Check**:
   ```bash
   curl https://your-app.railway.app/api/health/
   ```

2. **Test File Upload**:
   ```bash
   curl -X POST https://your-app.railway.app/api/apply/ \
     -F "file=@test.tsx" \
     -F "template_type=bt" \
     -F "return_file=false"
   ```

## Monitoring

Railway provides:
- **Logs**: View real-time logs in the dashboard
- **Metrics**: CPU, memory, and network usage
- **Health Checks**: Automatic health monitoring
- **Deployments**: Track deployment history

## Troubleshooting

### Common Issues

1. **Build Fails**:
   - Check Dockerfile syntax
   - Ensure all dependencies are in requirements.txt
   - Verify Python version compatibility

2. **App Won't Start**:
   - Check logs in Railway dashboard
   - Verify PORT environment variable usage
   - Ensure app binds to 0.0.0.0

3. **Health Check Fails**:
   - Verify `/api/health/` endpoint works
   - Check if app is listening on correct port

### Logs

View logs in Railway dashboard or via CLI:
```bash
railway logs
```

## Scaling

Railway automatically handles:
- **Load Balancing**: Multiple instances if needed
- **Auto-scaling**: Based on traffic
- **Zero-downtime Deployments**: Rolling updates

## Custom Domain

1. Go to your project settings
2. Add custom domain
3. Configure DNS records as instructed
4. SSL certificates are automatically provisioned

## Cost

Railway offers:
- **Free Tier**: $5 credit monthly
- **Pro Plan**: Pay-as-you-go pricing
- **Team Plan**: For organizations

Check [railway.app/pricing](https://railway.app/pricing) for current rates.

## Security

The Dockerfile includes:
- **Non-root User**: Runs as `app` user
- **Minimal Base Image**: Python slim image
- **No Debug Mode**: Production configuration
- **Health Checks**: Automatic monitoring

## Support

- **Railway Docs**: [docs.railway.app](https://docs.railway.app)
- **Community**: [Railway Discord](https://discord.gg/railway)
- **GitHub Issues**: For application-specific issues
