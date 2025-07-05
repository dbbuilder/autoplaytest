# Terraform Setup for AutoPlayTest on AWS Lambda

This guide provides complete instructions for deploying AutoPlayTest as a serverless application on AWS using Terraform.

## Architecture Overview

The Terraform configuration deploys:
- **Lambda Functions** for test execution
- **API Gateway** for REST API endpoints
- **S3 Buckets** for test results and artifacts
- **DynamoDB** for task tracking
- **SQS** for async job processing
- **CloudWatch** for logging and monitoring
- **Secrets Manager** for API keys
- **VPC** with NAT Gateway for Lambda internet access

## Prerequisites

1. **AWS Account** with appropriate permissions
2. **Terraform** installed (v1.5+)
3. **AWS CLI** configured with credentials
4. **Docker** for building Lambda layers
5. **Python 3.12** for local development

## Quick Start

```bash
# Navigate to terraform directory
cd terraform

# Initialize Terraform
terraform init

# Create terraform.tfvars file with your values
cp terraform.tfvars.example terraform.tfvars

# Plan the deployment
terraform plan

# Apply the configuration
terraform apply

# Get the API endpoint
terraform output api_endpoint
```

## Configuration

### 1. Environment Variables

Create `terraform/terraform.tfvars`:
```hcl
project_name = "autoplaytest"
environment  = "production"
region       = "us-east-1"

# API Keys (stored in AWS Secrets Manager)
anthropic_api_key = "your-anthropic-api-key"
openai_api_key    = "your-openai-api-key"
google_api_key    = "your-google-api-key"

# Optional configurations
lambda_memory_size = 3008  # Maximum for better performance
lambda_timeout     = 900   # 15 minutes
enable_xray       = true
enable_vpc       = true   # Required for Playwright
```

### 2. Backend Configuration

For team environments, configure S3 backend in `terraform/backend.tf`:
```hcl
terraform {
  backend "s3" {
    bucket = "your-terraform-state-bucket"
    key    = "autoplaytest/terraform.tfstate"
    region = "us-east-1"
    
    # Enable state locking
    dynamodb_table = "terraform-state-lock"
    encrypt        = true
  }
}
```

## Directory Structure

```
terraform/
├── main.tf                 # Main configuration
├── variables.tf            # Variable definitions
├── outputs.tf             # Output definitions
├── lambda.tf              # Lambda functions
├── api_gateway.tf         # API Gateway configuration
├── dynamodb.tf            # DynamoDB tables
├── s3.tf                  # S3 buckets
├── sqs.tf                 # SQS queues
├── vpc.tf                 # VPC configuration
├── iam.tf                 # IAM roles and policies
├── cloudwatch.tf          # Monitoring and alarms
├── secrets.tf             # Secrets Manager
├── lambda_layer.tf        # Lambda layers
├── terraform.tfvars.example
└── modules/
    ├── lambda_function/   # Reusable Lambda module
    └── api_endpoint/      # Reusable API endpoint module
```

## Lambda Functions

### Test Execution Function
- Handles individual test execution
- Memory: 3008 MB (maximum)
- Timeout: 15 minutes
- Includes Playwright binaries in Lambda layer

### API Handler Function
- Processes API requests
- Manages async job creation
- Returns job status

### Result Processor Function
- Processes test results
- Stores artifacts in S3
- Updates DynamoDB

## API Endpoints

The deployment creates these endpoints:

```
POST   /tests/run          # Run tests asynchronously
GET    /tests/{id}         # Get test status
GET    /tests              # List all tests
POST   /tests/generate     # Generate test scripts
DELETE /tests/{id}         # Cancel test
GET    /health             # Health check
```

## Building Lambda Layers

The Playwright binaries and dependencies need to be packaged as Lambda layers:

```bash
# Run the build script
cd terraform
./build_lambda_layers.sh

# Or manually:
docker run -v "$PWD":/var/task public.ecr.aws/lambda/python:3.12 /bin/sh -c "
  pip install -r /var/task/requirements-lambda.txt -t /var/task/layer/python/lib/python3.12/site-packages/
  cd /var/task/layer && zip -r ../lambda-layer.zip .
"
```

## Deployment Steps

### 1. First-time Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/autoplaytest.git
cd autoplaytest/terraform

# Install dependencies
pip install -r requirements-deploy.txt

# Initialize Terraform
terraform init

# Create and configure terraform.tfvars
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your values
```

### 2. Deploy Infrastructure

```bash
# Validate configuration
terraform validate

# Plan deployment
terraform plan -out=tfplan

# Apply configuration
terraform apply tfplan

# Save outputs
terraform output -json > outputs.json
```

### 3. Deploy Lambda Code

```bash
# Package Lambda functions
./package_lambdas.sh

# Update function code
terraform apply -target=aws_lambda_function.test_executor
terraform apply -target=aws_lambda_function.api_handler
```

## Monitoring and Logging

### CloudWatch Dashboards
- Lambda execution metrics
- API Gateway metrics
- Error rates and latencies
- Cost tracking

### Alarms
- High error rate
- Long execution times
- Failed test executions
- API throttling

### X-Ray Tracing
- End-to-end request tracing
- Performance bottleneck identification
- Service map visualization

## Cost Optimization

### Estimated Monthly Costs
- Lambda: ~$50-200 (depending on usage)
- API Gateway: ~$3.50 per million requests
- DynamoDB: ~$25 (on-demand mode)
- S3: ~$5-20 (depending on storage)
- CloudWatch: ~$10-30
- NAT Gateway: ~$45 (if VPC enabled)

### Cost Saving Tips
1. Use Lambda provisioned concurrency only for consistent workloads
2. Enable S3 lifecycle policies for old test results
3. Use DynamoDB auto-scaling
4. Consider Lambda@Edge for geographic distribution
5. Use SQS for batch processing

## Security Best Practices

1. **Secrets Management**
   - All API keys stored in AWS Secrets Manager
   - Automatic rotation enabled
   - Lambda functions access via IAM roles

2. **Network Security**
   - Lambda functions in private VPC subnets
   - NAT Gateway for outbound internet access
   - Security groups restrict access

3. **API Security**
   - API Gateway with API keys
   - Optional AWS WAF integration
   - Request throttling enabled

4. **Compliance**
   - CloudTrail logging enabled
   - S3 bucket encryption
   - DynamoDB encryption at rest

## Troubleshooting

### Common Issues

1. **Lambda Timeout**
   - Increase timeout in terraform.tfvars
   - Consider breaking tests into smaller chunks

2. **Memory Issues**
   - Lambda already at maximum (3008 MB)
   - Optimize test scripts

3. **Cold Start Latency**
   - Enable provisioned concurrency
   - Use Lambda SnapStart

4. **VPC Issues**
   - Ensure NAT Gateway is properly configured
   - Check security group rules

### Debug Commands

```bash
# View Lambda logs
aws logs tail /aws/lambda/autoplaytest-test-executor --follow

# Test Lambda function
aws lambda invoke \
  --function-name autoplaytest-test-executor \
  --payload '{"url":"https://example.com"}' \
  response.json

# Check API Gateway
curl -X POST https://your-api-id.execute-api.region.amazonaws.com/prod/tests/run \
  -H "Content-Type: application/json" \
  -d '{"url":"https://example.com"}'
```

## Maintenance

### Updates
```bash
# Update Terraform modules
terraform get -update

# Update Lambda layers
./build_lambda_layers.sh
terraform apply -target=aws_lambda_layer_version.playwright

# Update function code
./package_lambdas.sh
terraform apply
```

### Backup
```bash
# Backup DynamoDB
aws dynamodb create-backup \
  --table-name autoplaytest-tasks \
  --backup-name autoplaytest-backup-$(date +%Y%m%d)

# Export Terraform state
terraform state pull > terraform.tfstate.backup
```

### Destroy
```bash
# Remove all resources
terraform destroy

# Or selectively
terraform destroy -target=aws_lambda_function.test_executor
```

## CI/CD Integration

### GitHub Actions
```yaml
name: Deploy to AWS Lambda

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
      
      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v2
        
      - name: Terraform Init
        run: terraform init
        working-directory: ./terraform
        
      - name: Terraform Apply
        run: terraform apply -auto-approve
        working-directory: ./terraform
```

## Advanced Configuration

### Multi-Region Deployment
See `terraform/modules/multi_region/` for deploying across multiple AWS regions.

### Custom Domain
```hcl
# In api_gateway.tf
resource "aws_api_gateway_domain_name" "custom" {
  domain_name = "api.autoplaytest.com"
  
  endpoint_configuration {
    types = ["EDGE"]
  }
  
  certificate_arn = aws_acm_certificate.api.arn
}
```

### VPC Endpoints
For enhanced security, configure VPC endpoints for AWS services:
```hcl
# In vpc.tf
resource "aws_vpc_endpoint" "s3" {
  vpc_id       = aws_vpc.main.id
  service_name = "com.amazonaws.${var.region}.s3"
}
```

## Support

- GitHub Issues: https://github.com/yourusername/autoplaytest/issues
- AWS Support: https://console.aws.amazon.com/support/
- Terraform Registry: https://registry.terraform.io/