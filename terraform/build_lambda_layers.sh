#!/bin/bash

# Build Lambda layers for AutoPlayTest
# This script creates a Lambda layer with Playwright and all dependencies

set -e

echo "🔨 Building Lambda layers for AutoPlayTest..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is required but not installed${NC}"
    echo "Please install Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

# Create build directory
BUILD_DIR="lambda-layer-build"
rm -rf $BUILD_DIR
mkdir -p $BUILD_DIR

# Create requirements file for Lambda layer
cat > $BUILD_DIR/requirements-lambda.txt << EOF
# Core dependencies for Lambda
playwright==1.40.0
aiohttp==3.9.1
pydantic==2.5.0
python-dotenv==1.0.0
pyyaml==6.0.1
jinja2==3.1.2
anthropic==0.7.7
openai==1.3.0
google-generativeai==0.3.0
aiofiles==23.2.1
httpx==0.25.2
tenacity==8.2.3
beautifulsoup4==4.12.2
lxml==4.9.3
boto3==1.34.0
EOF

echo -e "${YELLOW}📦 Building Python dependencies layer...${NC}"

# Build the layer using Lambda Python runtime
docker run --rm \
  -v "$PWD/$BUILD_DIR":/var/task \
  -v "$PWD/../src":/var/task/src \
  -v "$PWD/../config":/var/task/config \
  public.ecr.aws/lambda/python:3.12 \
  /bin/sh -c "
    echo 'Installing dependencies...'
    pip install -r /var/task/requirements-lambda.txt -t /var/task/python/lib/python3.12/site-packages/ --no-cache-dir
    
    echo 'Copying source code...'
    cp -r /var/task/src /var/task/python/
    cp -r /var/task/config /var/task/python/
    
    echo 'Installing Playwright browsers...'
    cd /var/task/python/lib/python3.12/site-packages
    PLAYWRIGHT_BROWSERS_PATH=/var/task/python/browsers python -m playwright install chromium
    
    echo 'Creating layer zip...'
    cd /var/task
    zip -r ../lambda-layer.zip python/ -x '*.pyc' -x '__pycache__/*'
  "

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Lambda layer built successfully!${NC}"
    echo "Layer file: lambda-layer.zip"
    echo "Size: $(du -h lambda-layer.zip | cut -f1)"
else
    echo -e "${RED}❌ Failed to build Lambda layer${NC}"
    exit 1
fi

# Clean up
rm -rf $BUILD_DIR

echo -e "${GREEN}🎉 Build complete!${NC}"