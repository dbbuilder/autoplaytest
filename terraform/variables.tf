variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "autoplaytest"
}

variable "environment" {
  description = "Environment name (dev, staging, production)"
  type        = string
  default     = "production"
}

variable "region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "lambda_memory_size" {
  description = "Memory size for Lambda functions in MB"
  type        = number
  default     = 3008 # Maximum for better performance
}

variable "lambda_timeout" {
  description = "Timeout for Lambda functions in seconds"
  type        = number
  default     = 900 # 15 minutes
}

variable "enable_xray" {
  description = "Enable AWS X-Ray tracing"
  type        = bool
  default     = true
}

variable "enable_vpc" {
  description = "Deploy Lambda functions in VPC (required for Playwright)"
  type        = bool
  default     = true
}

variable "anthropic_api_key" {
  description = "Anthropic API key for Claude"
  type        = string
  sensitive   = true
}

variable "openai_api_key" {
  description = "OpenAI API key for GPT"
  type        = string
  sensitive   = true
}

variable "google_api_key" {
  description = "Google API key for Gemini"
  type        = string
  sensitive   = true
}

variable "api_rate_limit" {
  description = "API Gateway rate limit per second"
  type        = number
  default     = 100
}

variable "api_burst_limit" {
  description = "API Gateway burst limit"
  type        = number
  default     = 200
}

variable "dynamodb_read_capacity" {
  description = "DynamoDB read capacity units (0 for on-demand)"
  type        = number
  default     = 0
}

variable "dynamodb_write_capacity" {
  description = "DynamoDB write capacity units (0 for on-demand)"
  type        = number
  default     = 0
}

variable "s3_retention_days" {
  description = "Number of days to retain test results in S3"
  type        = number
  default     = 90
}

variable "enable_api_key" {
  description = "Require API key for API Gateway"
  type        = bool
  default     = true
}

variable "allowed_cidr_blocks" {
  description = "CIDR blocks allowed to access the API"
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

variable "tags" {
  description = "Tags to apply to all resources"
  type        = map(string)
  default = {
    Project     = "AutoPlayTest"
    ManagedBy   = "Terraform"
    Environment = "production"
  }
}

variable "lambda_reserved_concurrent_executions" {
  description = "Reserved concurrent executions for Lambda functions (-1 for no limit)"
  type        = number
  default     = -1
}

variable "enable_dead_letter_queue" {
  description = "Enable dead letter queue for failed Lambda invocations"
  type        = bool
  default     = true
}

variable "alarm_email" {
  description = "Email address for CloudWatch alarms"
  type        = string
  default     = ""
}

variable "log_retention_days" {
  description = "CloudWatch log retention in days"
  type        = number
  default     = 30
}