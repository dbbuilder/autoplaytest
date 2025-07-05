# DynamoDB table for task tracking
resource "aws_dynamodb_table" "tasks" {
  name         = "${local.prefix}-tasks"
  billing_mode = var.dynamodb_read_capacity == 0 ? "PAY_PER_REQUEST" : "PROVISIONED"
  
  read_capacity  = var.dynamodb_read_capacity == 0 ? null : var.dynamodb_read_capacity
  write_capacity = var.dynamodb_write_capacity == 0 ? null : var.dynamodb_write_capacity
  
  hash_key = "task_id"
  
  attribute {
    name = "task_id"
    type = "S"
  }
  
  attribute {
    name = "status"
    type = "S"
  }
  
  attribute {
    name = "created_at"
    type = "S"
  }
  
  attribute {
    name = "user_id"
    type = "S"
  }
  
  global_secondary_index {
    name            = "status-created_at-index"
    hash_key        = "status"
    range_key       = "created_at"
    projection_type = "ALL"
    read_capacity   = var.dynamodb_read_capacity == 0 ? null : var.dynamodb_read_capacity
    write_capacity  = var.dynamodb_write_capacity == 0 ? null : var.dynamodb_write_capacity
  }
  
  global_secondary_index {
    name            = "user_id-created_at-index"
    hash_key        = "user_id"
    range_key       = "created_at"
    projection_type = "ALL"
    read_capacity   = var.dynamodb_read_capacity == 0 ? null : var.dynamodb_read_capacity
    write_capacity  = var.dynamodb_write_capacity == 0 ? null : var.dynamodb_write_capacity
  }
  
  ttl {
    attribute_name = "ttl"
    enabled        = true
  }
  
  point_in_time_recovery {
    enabled = true
  }
  
  server_side_encryption {
    enabled = true
  }
  
  tags = {
    Name = "${local.prefix}-tasks"
  }
}

# DynamoDB table for test results
resource "aws_dynamodb_table" "test_results" {
  name         = "${local.prefix}-test-results"
  billing_mode = var.dynamodb_read_capacity == 0 ? "PAY_PER_REQUEST" : "PROVISIONED"
  
  read_capacity  = var.dynamodb_read_capacity == 0 ? null : var.dynamodb_read_capacity
  write_capacity = var.dynamodb_write_capacity == 0 ? null : var.dynamodb_write_capacity
  
  hash_key = "test_id"
  range_key = "timestamp"
  
  attribute {
    name = "test_id"
    type = "S"
  }
  
  attribute {
    name = "timestamp"
    type = "S"
  }
  
  attribute {
    name = "task_id"
    type = "S"
  }
  
  attribute {
    name = "test_type"
    type = "S"
  }
  
  global_secondary_index {
    name            = "task_id-index"
    hash_key        = "task_id"
    projection_type = "ALL"
    read_capacity   = var.dynamodb_read_capacity == 0 ? null : var.dynamodb_read_capacity
    write_capacity  = var.dynamodb_write_capacity == 0 ? null : var.dynamodb_write_capacity
  }
  
  global_secondary_index {
    name            = "test_type-timestamp-index"
    hash_key        = "test_type"
    range_key       = "timestamp"
    projection_type = "ALL"
    read_capacity   = var.dynamodb_read_capacity == 0 ? null : var.dynamodb_read_capacity
    write_capacity  = var.dynamodb_write_capacity == 0 ? null : var.dynamodb_write_capacity
  }
  
  server_side_encryption {
    enabled = true
  }
  
  tags = {
    Name = "${local.prefix}-test-results"
  }
}

# DynamoDB VPC Endpoint (if VPC is enabled)
resource "aws_vpc_endpoint" "dynamodb" {
  count = var.enable_vpc ? 1 : 0
  
  vpc_id            = aws_vpc.main[0].id
  service_name      = "com.amazonaws.${var.region}.dynamodb"
  vpc_endpoint_type = "Gateway"
  route_table_ids   = aws_route_table.private[*].id
  
  tags = {
    Name = "${local.prefix}-dynamodb-endpoint"
  }
}