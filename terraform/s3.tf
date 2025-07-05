# S3 bucket for test results and artifacts
resource "aws_s3_bucket" "results" {
  bucket = "${local.prefix}-results-${local.account_id}"
  
  tags = {
    Name = "${local.prefix}-results"
  }
}

# S3 bucket versioning
resource "aws_s3_bucket_versioning" "results" {
  bucket = aws_s3_bucket.results.id
  
  versioning_configuration {
    status = "Enabled"
  }
}

# S3 bucket encryption
resource "aws_s3_bucket_server_side_encryption_configuration" "results" {
  bucket = aws_s3_bucket.results.id
  
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# S3 bucket public access block
resource "aws_s3_bucket_public_access_block" "results" {
  bucket = aws_s3_bucket.results.id
  
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# S3 bucket lifecycle configuration
resource "aws_s3_bucket_lifecycle_configuration" "results" {
  bucket = aws_s3_bucket.results.id
  
  rule {
    id     = "delete-old-results"
    status = "Enabled"
    
    expiration {
      days = var.s3_retention_days
    }
    
    noncurrent_version_expiration {
      noncurrent_days = 30
    }
  }
  
  rule {
    id     = "transition-to-glacier"
    status = "Enabled"
    
    transition {
      days          = 30
      storage_class = "GLACIER"
    }
  }
}

# S3 bucket for Lambda deployment packages
resource "aws_s3_bucket" "lambda_deployments" {
  bucket = "${local.prefix}-lambda-deployments-${local.account_id}"
  
  tags = {
    Name = "${local.prefix}-lambda-deployments"
  }
}

# S3 bucket versioning for deployments
resource "aws_s3_bucket_versioning" "lambda_deployments" {
  bucket = aws_s3_bucket.lambda_deployments.id
  
  versioning_configuration {
    status = "Enabled"
  }
}

# S3 bucket encryption for deployments
resource "aws_s3_bucket_server_side_encryption_configuration" "lambda_deployments" {
  bucket = aws_s3_bucket.lambda_deployments.id
  
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# S3 bucket public access block for deployments
resource "aws_s3_bucket_public_access_block" "lambda_deployments" {
  bucket = aws_s3_bucket.lambda_deployments.id
  
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# S3 VPC Endpoint (if VPC is enabled)
resource "aws_vpc_endpoint" "s3" {
  count = var.enable_vpc ? 1 : 0
  
  vpc_id            = aws_vpc.main[0].id
  service_name      = "com.amazonaws.${var.region}.s3"
  vpc_endpoint_type = "Gateway"
  route_table_ids   = aws_route_table.private[*].id
  
  tags = {
    Name = "${local.prefix}-s3-endpoint"
  }
}

# S3 bucket notification configuration for result processing
resource "aws_s3_bucket_notification" "results" {
  bucket = aws_s3_bucket.results.id
  
  queue {
    queue_arn     = aws_sqs_queue.result_queue.arn
    events        = ["s3:ObjectCreated:*"]
    filter_prefix = "test-results/"
  }
  
  depends_on = [aws_sqs_queue_policy.s3_to_sqs]
}