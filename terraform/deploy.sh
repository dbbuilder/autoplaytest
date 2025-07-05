#!/bin/bash

# Complete deployment script for AutoPlayTest on AWS Lambda
# This script handles the entire deployment process

set -e

echo "🚀 AutoPlayTest AWS Lambda Deployment"
echo "====================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check prerequisites
check_prerequisites() {
    echo -e "${YELLOW}Checking prerequisites...${NC}"
    
    # Check Terraform
    if ! command -v terraform &> /dev/null; then
        echo -e "${RED}❌ Terraform is not installed${NC}"
        echo "Install from: https://www.terraform.io/downloads"
        exit 1
    fi
    
    # Check AWS CLI
    if ! command -v aws &> /dev/null; then
        echo -e "${RED}❌ AWS CLI is not installed${NC}"
        echo "Install from: https://aws.amazon.com/cli/"
        exit 1
    fi
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker is not installed${NC}"
        echo "Install from: https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        echo -e "${RED}❌ AWS credentials not configured${NC}"
        echo "Run: aws configure"
        exit 1
    fi
    
    echo -e "${GREEN}✅ All prerequisites met${NC}"
}

# Build Lambda layers
build_layers() {
    echo -e "\n${YELLOW}Building Lambda layers...${NC}"
    ./build_lambda_layers.sh
}

# Package Lambda functions
package_functions() {
    echo -e "\n${YELLOW}Packaging Lambda functions...${NC}"
    ./package_lambdas.sh
}

# Initialize Terraform
init_terraform() {
    echo -e "\n${YELLOW}Initializing Terraform...${NC}"
    terraform init
}

# Validate Terraform configuration
validate_terraform() {
    echo -e "\n${YELLOW}Validating Terraform configuration...${NC}"
    terraform validate
}

# Plan deployment
plan_deployment() {
    echo -e "\n${YELLOW}Planning deployment...${NC}"
    terraform plan -out=tfplan
}

# Apply deployment
apply_deployment() {
    echo -e "\n${YELLOW}Applying deployment...${NC}"
    terraform apply tfplan
}

# Display outputs
show_outputs() {
    echo -e "\n${BLUE}Deployment Outputs:${NC}"
    terraform output -json | jq '.'
    
    echo -e "\n${GREEN}🎉 Deployment complete!${NC}"
    echo -e "\n${BLUE}API Endpoint:${NC}"
    terraform output -raw api_endpoint
    
    if [ "$(terraform output -raw api_key 2>/dev/null)" != "" ]; then
        echo -e "\n${BLUE}API Key:${NC}"
        terraform output -raw api_key
    fi
    
    echo -e "\n${BLUE}Next steps:${NC}"
    echo "1. Test the health endpoint:"
    echo "   curl $(terraform output -raw api_endpoint)/health"
    echo ""
    echo "2. Run a test:"
    echo "   curl -X POST $(terraform output -raw api_endpoint)/tests/run \\"
    echo "     -H 'Content-Type: application/json' \\"
    if [ "$(terraform output -raw api_key 2>/dev/null)" != "" ]; then
        echo "     -H 'x-api-key: $(terraform output -raw api_key)' \\"
    fi
    echo "     -d '{\"url\": \"https://example.com\"}'"
}

# Main deployment flow
main() {
    # Check if terraform.tfvars exists
    if [ ! -f "terraform.tfvars" ]; then
        echo -e "${YELLOW}No terraform.tfvars found. Creating from example...${NC}"
        cp terraform.tfvars.example terraform.tfvars
        echo -e "${RED}Please edit terraform.tfvars with your API keys and configuration${NC}"
        exit 1
    fi
    
    # Run deployment steps
    check_prerequisites
    build_layers
    package_functions
    init_terraform
    validate_terraform
    plan_deployment
    
    # Confirm before applying
    echo -e "\n${YELLOW}Ready to deploy. Review the plan above.${NC}"
    read -p "Continue with deployment? (y/n) " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        apply_deployment
        show_outputs
    else
        echo -e "${RED}Deployment cancelled${NC}"
        exit 1
    fi
}

# Run main function
main