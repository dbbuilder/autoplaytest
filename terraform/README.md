# AutoPlayTest Terraform Deployment

This directory contains the complete Terraform configuration for deploying AutoPlayTest on AWS Lambda.

## Quick Start

1. **Configure AWS credentials:**
   ```bash
   aws configure
   ```

2. **Copy and edit configuration:**
   ```bash
   cp terraform.tfvars.example terraform.tfvars
   # Edit terraform.tfvars with your API keys
   ```

3. **Run deployment:**
   ```bash
   ./deploy.sh
   ```

## Manual Deployment

If you prefer to run steps manually:

```bash
# Build Lambda layers
./build_lambda_layers.sh

# Package Lambda functions
./package_lambdas.sh

# Initialize Terraform
terraform init

# Plan deployment
terraform plan

# Apply deployment
terraform apply
```

## Files Overview

- `main.tf` - Main Terraform configuration
- `variables.tf` - Variable definitions
- `lambda.tf` - Lambda function configurations
- `api_gateway.tf` - API Gateway setup
- `dynamodb.tf` - DynamoDB tables
- `s3.tf` - S3 buckets for results
- `vpc.tf` - VPC configuration for Lambda
- `iam.tf` - IAM roles and policies
- `secrets.tf` - Secrets Manager configuration
- `terraform.tfvars.example` - Example configuration file

## Architecture

The deployment creates:

```
┌─────────────────┐     ┌──────────────┐     ┌─────────────────┐
│   API Gateway   │────▶│ API Handler  │────▶│ Test Executor   │
│  (REST API)     │     │  (Lambda)    │     │   (Lambda)      │
└─────────────────┘     └──────────────┘     └─────────────────┘
                                │                      │
                                ▼                      ▼
                        ┌──────────────┐      ┌─────────────────┐
                        │  DynamoDB    │      │   S3 Bucket     │
                        │   (Tasks)    │      │  (Results)      │
                        └──────────────┘      └─────────────────┘
                                                       │
                                                       ▼
                                              ┌─────────────────┐
                                              │Result Processor │
                                              │   (Lambda)      │
                                              └─────────────────┘
```

## API Endpoints

After deployment, these endpoints are available:

- `GET /health` - Health check
- `POST /tests/run` - Run tests asynchronously
- `GET /tests/{id}` - Get test status
- `GET /tests` - List all tests
- `POST /tests/generate` - Generate test scripts
- `DELETE /tests/{id}` - Cancel test

## Cost Estimates

- Lambda: ~$0.0000166667 per GB-second
- API Gateway: $3.50 per million requests
- DynamoDB: On-demand pricing
- S3: $0.023 per GB/month
- NAT Gateway: ~$45/month (if VPC enabled)

## Monitoring

CloudWatch dashboards are automatically created for:
- Lambda execution metrics
- API Gateway performance
- Error rates and alerts
- Cost tracking

## Troubleshooting

### Lambda timeout issues
- Increase `lambda_timeout` in terraform.tfvars
- Maximum is 900 seconds (15 minutes)

### Memory issues
- Already set to maximum (3008 MB)
- Optimize test scripts if needed

### VPC connectivity
- Ensure NAT Gateway is properly configured
- Check security group rules

## Cleanup

To remove all resources:

```bash
terraform destroy
```

## Support

For issues or questions:
- Check CloudWatch logs
- Review terraform plan output
- Open GitHub issue