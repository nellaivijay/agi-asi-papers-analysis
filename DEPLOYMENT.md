# AGI/ASI Papers Analysis - Deployment Guide

This guide covers deployment options for the AGI/ASI Papers Analysis tool, including local deployment, cloud deployment, and Hugging Face Spaces.

## 🎓 Educational Purpose

This tool is created for educational purposes to demonstrate AGI/ASI research tracking and analysis deployment strategies.

## Deployment Options

### 1. Local Deployment

**Best for**: Development, testing, personal use

**Pros**:
- Full control over environment
- No hosting costs
- Privacy (data stays local)
- Easy to set up

**Cons**:
- Not accessible from outside your network
- Requires your machine to be running
- Limited scalability

**Steps**:
1. Follow the [Installation Guide](INSTALLATION.md)
2. Run: `python app.py`
3. Access at: `http://localhost:7860`

**Network Access**:
To access from other devices on your network:
```bash
python app.py --server_name 0.0.0.0 --server_port 7860
```

### 2. Hugging Face Spaces (Recommended)

**Best for**: Public sharing, educational demos, easy deployment

**Pros**:
- Free hosting for public spaces
- Easy deployment from GitHub
- Built-in Gradio support
- No server management required

**Cons**:
- Limited resources on free tier
- Public by default
- Rate limits on free tier

#### Steps for Hugging Face Spaces Deployment

1. **Create a Hugging Face Account**
   - Go to https://huggingface.co/join
   - Create your free account

2. **Create a New Space**
   - Go to https://huggingface.co/spaces
   - Click "Create new Space"
   - Choose:
     - **Owner**: Your username
     - **Space name**: `agi-asi-papers-analysis`
     - **License**: MIT
     - **SDK**: Gradio
     - **Hardware**: CPU Basic (free) or upgrade if needed

3. **Prepare Your Repository**
   - Ensure your code is on GitHub
   - Add a `README.md` with proper metadata (see below)
   - Include `requirements.txt`
   - Add `.gitignore` for Python projects

4. **Connect Space to GitHub**
   - In your Space settings, select "Connect to GitHub"
   - Choose your repository
   - Select the branch to deploy

5. **Add Space-Specific Files**

   Create or update `README.md` with:
   ```markdown
   ---
   title: AGI/ASI Papers Analysis
   emoji: 🧠
   colorFrom: purple
   colorTo: blue
   sdk: gradio
   sdk_version: 4.44.1
   app_file: app.py
   pinned: false
   license: mit
   ---
   
   # AGI/ASI Papers Analysis
   
   Analyze AI papers for AGI/ASI relevance using multiple AI models.
   
   ## 🎓 Educational Purpose
   This tool is created for educational purposes.
   ```

6. **Environment Variables** (for API keys)
   - In Space Settings → Variables
   - Add your API keys:
     - `OPENAI_API_KEY` (if using OpenAI)
     - `ANTHROPIC_API_KEY` (if using Anthropic)
     - `HUGGINGFACE_API_KEY` (if using Hugging Face)

7. **Deploy**
   - Push your changes to GitHub
   - Hugging Face will automatically build and deploy
   - Monitor the build logs in the Space

8. **Access Your Space**
   - URL will be: `https://huggingface.co/spaces/YOUR_USERNAME/agi-asi-papers-analysis`

#### Hugging Face Space Configuration

For `requirements.txt` in Hugging Face Spaces, ensure:
```txt
requests==2.31.0
gradio==4.44.1
pandas==2.0.3
numpy==1.24.3
plotly==5.17.0
markdown==3.5.1
openai==1.12.0
anthropic==0.18.0
```

#### Troubleshooting Hugging Face Spaces

- **Build fails**: Check the build logs for dependency issues
- **App crashes**: Review runtime logs in the Space
- **Slow performance**: Consider upgrading to a paid hardware tier
- **API key errors**: Ensure environment variables are set correctly

### 3. Docker Deployment

**Best for**: Production environments, custom infrastructure

**Pros**:
- Consistent environment
- Easy to scale
- Works with any hosting provider
- Version control for dependencies

**Cons**:
- Requires Docker knowledge
- More complex setup
- Ongoing maintenance

#### Dockerfile

Create `Dockerfile`:
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 7860

CMD ["python", "app.py"]
```

#### Build and Run

```bash
# Build image
docker build -t agi-asi-analysis .

# Run container
docker run -p 7860:7860 \
  -e OPENAI_API_KEY=your_key \
  agi-asi-analysis
```

#### Docker Compose

Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "7860:7860"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    restart: unless-stopped
```

Run with:
```bash
docker-compose up -d
```

### 4. Cloud Deployment (AWS/GCP/Azure)

**Best for**: Enterprise use, high scalability, custom requirements

#### AWS Deployment

**Option 1: EC2**
1. Launch EC2 instance (t3.medium or higher)
2. Install Docker and Docker Compose
3. Deploy using Docker Compose
4. Configure security group for port 7860
5. Set up domain and SSL (optional)

**Option 2: ECS**
1. Create ECR repository
2. Push Docker image
3. Create ECS task definition
4. Set up ECS service with load balancer

**Option 3: Lambda + API Gateway**
1. Package application for Lambda
2. Set up API Gateway
3. Configure Lambda function
4. Use Gradio's serverless mode

#### Google Cloud Deployment

**Option 1: Cloud Run**
```bash
# Build and push to GCR
gcloud builds submit --tag gcr.io/PROJECT_ID/agi-asi-analysis

# Deploy to Cloud Run
gcloud run deploy agi-asi-analysis \
  --image gcr.io/PROJECT_ID/agi-asi-analysis \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

**Option 2: Compute Engine**
1. Create Compute Engine instance
2. Deploy using Docker
3. Configure firewall rules
4. Set up load balancer (optional)

#### Azure Deployment

**Option 1: Container Instances**
```bash
# Create resource group
az group create --name agi-asi-rg --location eastus

# Create container instance
az container create \
  --resource-group agi-asi-rg \
  --name agi-asi-app \
  --image your-registry/agi-asi-analysis \
  --ports 7860 \
  --environment-variables OPENAI_API_KEY=your_key
```

**Option 2: Azure Container Apps**
1. Create Container Apps environment
2. Deploy container image
3. Configure ingress and scaling

### 5. Heroku Deployment

**Best for**: Quick deployment, moderate traffic

**Pros**:
- Easy setup
- Built-in SSL
- Automatic scaling
- Free tier available

**Cons**:
- Limited free tier
- Cold starts on free tier
- Less control than VPS

#### Steps

1. **Install Heroku CLI**
   ```bash
   # On Mac
   brew tap heroku/brew && brew install heroku

   # On Windows
   # Download from https://devcenter.heroku.com/articles/heroku-cli
   ```

2. **Login**
   ```bash
   heroku login
   ```

3. **Create Procfile**
   Create `Procfile`:
   ```
   web: python app.py
   ```

4. **Deploy**
   ```bash
   heroku create agi-asi-analysis
   git push heroku main
   heroku open
   ```

5. **Set Environment Variables**
   ```bash
   heroku config:set OPENAI_API_KEY=your_key
   heroku config:set ANTHROPIC_API_KEY=your_key
   ```

## Security Considerations

### API Key Management

**Never commit API keys to repositories!**

**Best practices**:
1. Use environment variables
2. Use secret management services (AWS Secrets Manager, Azure Key Vault)
3. Rotate keys regularly
4. Use least privilege access
5. Monitor API usage for anomalies

### Rate Limiting

Implement rate limiting for production:
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/analyze")
@limiter.limit("10/minute")
async def analyze(request: Request):
    # Your analysis logic
    pass
```

### Authentication

For private deployments, add authentication:
```python
import gradio as gr

def auth(username, password):
    return username == "admin" and password == "secure_password"

demo = create_interface()
demo.launch(auth=auth)
```

## Monitoring and Logging

### Application Monitoring

**Health Checks**:
```python
@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.now()}
```

**Metrics Collection**:
- Track API usage
- Monitor response times
- Log classification results
- Track error rates

### Logging

Set up proper logging:
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
```

## Performance Optimization

### Caching

Implement caching for frequently accessed data:
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def fetch_year_data_cached(year):
    return fetcher.fetch_year_data(year)
```

### Database Integration

For production, consider adding a database:
- Store classification results
- Track user queries
- Enable historical analysis

### CDN for Static Assets

Serve static files through CDN:
- Faster load times
- Reduced server load
- Better global performance

## Cost Estimation

### Hugging Face Spaces (Free Tier)
- Cost: $0/month
- Limitations: CPU Basic, public only
- Suitable for: Educational demos, low traffic

### Hugging Face Spaces (Paid)
- Cost: ~$0.10-$0.50/hour depending on hardware
- Suitable for: Higher traffic, private spaces

### AWS EC2
- t3.medium: ~$30/month
- t3.large: ~$60/month
- Suitable for: Production workloads

### Google Cloud Run
- Free tier: 2 million requests/month
- Paid: ~$0.40 per 1 million requests
- Suitable for: Variable workloads

### Heroku
- Eco: $5/month
- Basic: $7/month
- Standard: $25/month
- Suitable for: Small to medium applications

## Backup and Recovery

### Database Backups
- Regular automated backups
- Point-in-time recovery
- Cross-region replication

### Code Backups
- Git repository (GitHub/GitLab)
- Tag releases
- Maintain rollback capability

### Configuration Backups
- Version control configuration files
- Document environment variables
- Backup API keys securely

## Maintenance

### Regular Tasks
- Update dependencies
- Monitor API usage
- Review logs for errors
- Update keyword lists
- Test new AI models

### Updates and Patches
- Security updates
- Feature enhancements
- Bug fixes
- Model improvements

## Support and Troubleshooting

### Common Issues

1. **Application won't start**
   - Check logs for errors
   - Verify dependencies are installed
   - Check port availability

2. **API key errors**
   - Verify environment variables
   - Check API key validity
   - Review API quotas

3. **Slow performance**
   - Monitor resource usage
   - Consider upgrading hardware
   - Implement caching

4. **Deployment failures**
   - Review build logs
   - Check configuration files
   - Verify dependencies

---

**Note**: This tool is for educational purposes. Choose deployment options based on your specific needs and budget.
