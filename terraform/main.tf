terraform {
  required_version = ">= 1.5"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.4"
    }
  }
}

provider "aws" {
  region = var.region
  
  default_tags {
    tags = merge(var.tags, {
      Environment = var.environment
      Project     = var.project_name
    })
  }
}

# Data sources
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

locals {
  account_id = data.aws_caller_identity.current.account_id
  region     = data.aws_region.current.name
  
  # Naming convention
  prefix = "${var.project_name}-${var.environment}"
  
  # Lambda environment variables
  lambda_env_vars = {
    ENVIRONMENT         = var.environment
    REGION             = local.region
    PROJECT_NAME       = var.project_name
    DYNAMODB_TABLE     = aws_dynamodb_table.tasks.name
    S3_BUCKET          = aws_s3_bucket.results.id
    SQS_QUEUE_URL      = aws_sqs_queue.test_queue.url
    LOG_LEVEL          = "INFO"
    PYTHONPATH         = "/opt/python:/var/runtime:/var/task"
  }
}