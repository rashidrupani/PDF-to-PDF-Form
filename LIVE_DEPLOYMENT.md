# How to Deploy Simple AI Document Processor and Get a Live URL

This guide will show you how to deploy the Simple AI Document Processor and make it accessible via a live URL on the internet.

## Quick Deployment Options

### Option 1: Render.com (Recommended for beginners)

1. **Sign up for Render** at https://render.com
2. **Create a new Web Service**:
   - Connect to your GitHub repository
   - Choose the branch to deploy
   - Set the runtime to "Docker"
   - Use the Dockerfile in the backend directory

3. **Create a render.yaml** file in your repository:
```yaml
services:
  - type: web
    name: ai-document-processor
    env: docker
    dockerfilePath: backend/Dockerfile
    envVars:
      - key: ENVIRONMENT
        value: production
      - key: DEBUG
        value: "False"
      - key: MAX_FILE_SIZE
        value: "52428800"
    disk:
      name: uploads
      mountPath: /app/uploads
      sizeGB: 10
```

4. **Deploy** and get your live URL like: `https://your-app-name.onrender.com`

### Option 2: Heroku (Easy deployment)

1. **Sign up for Heroku** at https://heroku.com
2. **Install Heroku CLI** from https://devcenter.heroku.com/articles/heroku-cli
3. **Create a new app**:
```bash
heroku login
heroku create your-app-name
heroku stack:set container
git push heroku main
```

4. **Get your live URL**: `https://your-app-name.herokuapp.com`

### Option 3: Railway.app (Modern alternative)

1. **Sign up for Railway** at https://railway.app
2. **Create a new project** and connect to your GitHub repo
3. **Deploy using the Dockerfile** in the backend directory
4. **Configure environment variables**:
   - ENVIRONMENT = production
   - DEBUG = False
   - MAX_FILE_SIZE = 52428800

5. **Get your live URL** after deployment

### Option 4: Google Cloud Run (For more control)

1. **Sign up for Google Cloud** at https://cloud.google.com
2. **Enable Cloud Run API**
3. **Install Google Cloud SDK**
4. **Deploy with command line**:
```bash
gcloud run deploy ai-document-processor \
  --source . \
  --platform managed \
  --port 8000 \
  --memory 4Gi \
  --cpu 2 \
  --set-env-vars ENVIRONMENT=production,DEBUG=False,MAX_FILE_SIZE=52428800 \
  --allow-unauthenticated
```

## Step-by-Step Guide for Render.com

### Step 1: Prepare Your Repository
1. Create a GitHub repository with your application code
2. Make sure you have the Dockerfile in the backend directory
3. Ensure your main.py is in the backend directory

### Step 2: Deploy on Render
1. Go to https://render.com and sign up/in
2. Click "New +" and select "Web Service"
3. Connect to your GitHub account
4. Select your repository
5. Choose the branch to deploy (usually "main" or "master")
6. Render should automatically detect it's a Docker project
7. Set the build command to use your Dockerfile
8. Add environment variables:
   - ENVIRONMENT: production
   - DEBUG: False
   - MAX_FILE_SIZE: 52428800

### Step 3: Configure Resources
- **Region**: Choose closest to your users
- **Instance Type**: Start with Standard (1GB RAM, 1 CPU)
- **For heavy OCR processing, consider upgrading to 2GB+ RAM**

### Step 4: Deploy and Access
1. Click "Create Web Service"
2. Wait for the build to complete (10-15 minutes for first build)
3. Once complete, you'll get a URL like: `https://your-app-name.onrender.com`

## Alternative: One-Click Deployment Services

### Using Vercel (Frontend) + Railway (Backend)
1. Deploy frontend to Vercel
2. Deploy backend to Railway
3. Configure CORS between them

### Using Netlify Functions
1. Host frontend on Netlify
2. Use Netlify Functions for backend API
3. More complex but possible

## Manual Deployment to VPS (Most Control)

### Step 1: Get a VPS
- **DigitalOcean**: $5/month droplet (minimum)
- **Linode**: $5/month instance
- **AWS EC2**: Free tier available
- **Google Cloud**: Free tier available

### Step 2: SSH into your server
```bash
ssh root@your-server-ip
```

### Step 3: Install Docker
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
```

### Step 4: Clone and Deploy
```bash
git clone https://github.com/your-username/your-repo.git
cd web-ai-document-processor-simple
docker-compose up -d
```

### Step 5: Set up Nginx and SSL
```bash
apt update
apt install nginx certbot python3-certbot-nginx
```

### Step 6: Configure domain
- Point your domain to the server IP
- Configure Nginx reverse proxy

## Getting a Custom Domain

### For Platform Deployments:
1. Most platforms allow custom domains in settings
2. Add your domain in the platform dashboard
3. Update DNS settings to point to the platform

### For VPS:
1. Purchase a domain from any registrar
2. Point A record to your server IP
3. Set up SSL with Let's Encrypt

## Performance Considerations

### For OCR Processing:
- **Minimum**: 2GB RAM, 1 CPU
- **Recommended**: 4GB+ RAM, 2+ CPU for better performance
- **For production**: 8GB+ RAM, 4+ CPU

### Memory Requirements:
- OCR processing is memory-intensive
- Each document can require 500MB-2GB depending on size
- Plan accordingly for concurrent users

## Monitoring Your Deployment

### Check if your app is running:
```bash
# If using Docker
docker-compose ps

# Check logs
docker-compose logs backend
```

### Health Check:
- Visit: `https://your-domain.com/health`
- Should return: `{"status": "healthy", "timestamp": "..."}`

## Troubleshooting Common Issues

### If the app crashes or is slow:
1. Check memory usage
2. Increase server resources
3. Reduce MAX_FILE_SIZE if needed

### If uploads fail:
1. Check MAX_FILE_SIZE setting
2. Verify upload directory permissions
3. Ensure sufficient disk space

### If OCR results are poor:
1. This is normal for complex documents
2. Consider preprocessing documents
3. Adjust confidence thresholds

## Cost Estimates

### Platform Options:
- **Render**: $7-25/month depending on instance size
- **Heroku**: $5-25/month (container-based)
- **Railway**: $5-20/month
- **VPS**: $5-50/month depending on specs

### For Basic Usage (1-10 documents/day):
- **Render**: $7/month (free tier available)
- **Heroku**: $5/month
- **VPS**: $5/month

### For Production (100+ documents/day):
- **Render**: $15-25/month
- **VPS**: $10-30/month (more cost-effective)

## Final Steps

1. **Test your deployment** by uploading a sample document
2. **Verify all features work** (upload, processing, export)
3. **Set up monitoring** if needed
4. **Configure backups** for important data
5. **Set up custom domain** if desired

Your application will be accessible at the URL provided by your hosting platform, and users can access it from anywhere on the internet!

**Note**: OCR processing may take 1-5 minutes per document depending on complexity and server resources.