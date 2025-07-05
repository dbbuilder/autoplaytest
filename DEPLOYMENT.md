# Deployment Guide for AutoPlayTest

This guide covers various deployment options for the AutoPlayTest library.

## Option 1: PyPI Distribution (Recommended for Libraries)

### Prerequisites
1. Create accounts on:
   - [PyPI](https://pypi.org/account/register/)
   - [Test PyPI](https://test.pypi.org/account/register/) (for testing)

2. Install build tools:
```bash
pip install build twine
```

### Build and Upload
```bash
# Build the distribution
python -m build

# Upload to Test PyPI first
python -m twine upload --repository testpypi dist/*

# Test installation
pip install -i https://test.pypi.org/simple/ autoplaytest

# Upload to PyPI
python -m twine upload dist/*
```

### Users can then install with:
```bash
pip install autoplaytest
```

## Option 2: GitHub Repository

### Setup
1. Create a GitHub repository
2. Push your code:
```bash
git remote add origin https://github.com/yourusername/autoplaytest.git
git branch -M main
git push -u origin main
```

### GitHub Actions CI/CD
The `.github/workflows/ci.yml` file provides:
- Automated testing on multiple Python versions
- Code coverage reporting
- Automatic PyPI deployment on release

### Installation from GitHub
```bash
# Latest version
pip install git+https://github.com/yourusername/autoplaytest.git

# Specific version/tag
pip install git+https://github.com/yourusername/autoplaytest.git@v0.1.0
```

## Option 3: Docker Distribution

### Create Dockerfile
```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN playwright install --with-deps chromium

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 testuser && chown -R testuser:testuser /app
USER testuser

# Entry point
ENTRYPOINT ["python", "-m", "src.simple_runner"]
```

### Build and Push to Docker Hub
```bash
# Build image
docker build -t yourusername/autoplaytest:latest .

# Test locally
docker run -it yourusername/autoplaytest:latest --help

# Push to Docker Hub
docker login
docker push yourusername/autoplaytest:latest
```

### Users can run with:
```bash
docker run -v $(pwd)/tests:/app/tests yourusername/autoplaytest:latest \
  --url https://example.com \
  --username user \
  --password pass
```

## Option 4: Serverless Deployment (AWS Lambda)

### Create Lambda deployment package
```python
# lambda_handler.py
import json
import asyncio
from src.simple_runner import run_test_suite

def lambda_handler(event, context):
    """AWS Lambda handler"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        results = loop.run_until_complete(
            run_test_suite(
                url=event['url'],
                username=event.get('username'),
                password=event.get('password'),
                test_types=event.get('test_types', ['login'])
            )
        )
        
        return {
            'statusCode': 200,
            'body': json.dumps(results)
        }
    finally:
        loop.close()
```

### Deploy with Serverless Framework
```yaml
# serverless.yml
service: autoplaytest

provider:
  name: aws
  runtime: python3.12
  timeout: 900

functions:
  runTests:
    handler: lambda_handler.lambda_handler
    memorySize: 3008
    events:
      - http:
          path: /test
          method: post

plugins:
  - serverless-python-requirements

custom:
  pythonRequirements:
    dockerizePip: true
    layer: true
```

## Option 5: API Service Deployment

### Using FastAPI (already included)
```python
# api_server.py
from fastapi import FastAPI, BackgroundTasks
from src.simple_runner import run_test_suite
import asyncio

app = FastAPI(title="AutoPlayTest API")

@app.post("/run-tests")
async def run_tests(
    url: str,
    username: str = None,
    password: str = None,
    test_types: list = None,
    background_tasks: BackgroundTasks = None
):
    """Run tests asynchronously"""
    task_id = str(uuid.uuid4())
    
    # Run in background
    background_tasks.add_task(
        run_test_suite,
        url=url,
        username=username,
        password=password,
        test_types=test_types
    )
    
    return {"task_id": task_id, "status": "started"}
```

### Deploy to Cloud Platforms

#### Heroku
```bash
# Create Procfile
echo "web: uvicorn api_server:app --host 0.0.0.0 --port $PORT" > Procfile

# Deploy
heroku create autoplaytest-api
git push heroku main
```

#### Google Cloud Run
```bash
# Build container
gcloud builds submit --tag gcr.io/PROJECT-ID/autoplaytest

# Deploy
gcloud run deploy autoplaytest \
  --image gcr.io/PROJECT-ID/autoplaytest \
  --platform managed \
  --allow-unauthenticated
```

#### Azure Container Instances
```bash
# Create container registry
az acr create --resource-group myResourceGroup \
  --name autoplaytestregistry --sku Basic

# Build and push
az acr build --registry autoplaytestregistry \
  --image autoplaytest:v1 .

# Deploy
az container create \
  --resource-group myResourceGroup \
  --name autoplaytest \
  --image autoplaytestregistry.azurecr.io/autoplaytest:v1
```

## Option 6: Kubernetes Deployment

### Create Kubernetes manifests
```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: autoplaytest
spec:
  replicas: 3
  selector:
    matchLabels:
      app: autoplaytest
  template:
    metadata:
      labels:
        app: autoplaytest
    spec:
      containers:
      - name: autoplaytest
        image: yourusername/autoplaytest:latest
        ports:
        - containerPort: 8000
        env:
        - name: ANTHROPIC_API_KEY
          valueFrom:
            secretKeyRef:
              name: autoplaytest-secrets
              key: anthropic-api-key
---
apiVersion: v1
kind: Service
metadata:
  name: autoplaytest-service
spec:
  selector:
    app: autoplaytest
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8000
  type: LoadBalancer
```

### Deploy
```bash
# Create secrets
kubectl create secret generic autoplaytest-secrets \
  --from-literal=anthropic-api-key=$ANTHROPIC_API_KEY

# Apply manifests
kubectl apply -f deployment.yaml

# Check status
kubectl get pods
kubectl get services
```

## Environment Variables

For all deployment methods, ensure these environment variables are set:
- `ANTHROPIC_API_KEY` - For Claude AI provider
- `OPENAI_API_KEY` - For GPT provider
- `GOOGLE_API_KEY` - For Gemini provider

## Security Considerations

1. **API Keys**: Never commit API keys to version control
2. **Secrets Management**: Use platform-specific secret management:
   - AWS: Secrets Manager
   - GCP: Secret Manager
   - Azure: Key Vault
   - Kubernetes: Secrets
3. **Network Security**: Restrict access to necessary IPs/services
4. **Authentication**: Implement API authentication for public endpoints

## Monitoring and Logging

1. **Application Monitoring**:
   - Use APM tools (New Relic, DataDog, etc.)
   - Implement health checks
   - Set up alerts

2. **Logging**:
   - Centralize logs (ELK stack, CloudWatch, etc.)
   - Include request IDs for tracing
   - Log test execution metrics

## Cost Optimization

1. **Serverless**: Best for sporadic usage
2. **Container Services**: Good for consistent load
3. **Kubernetes**: Best for high scale with auto-scaling
4. **Consider**: Browser resource usage in containers

## Support and Documentation

- GitHub Issues: https://github.com/yourusername/autoplaytest/issues
- Documentation: https://autoplaytest.readthedocs.io
- PyPI: https://pypi.org/project/autoplaytest