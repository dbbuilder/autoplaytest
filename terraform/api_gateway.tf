# API Gateway REST API
resource "aws_api_gateway_rest_api" "main" {
  name        = "${local.prefix}-api"
  description = "AutoPlayTest API for test execution"
  
  endpoint_configuration {
    types = ["REGIONAL"]
  }
}

# API Resources
resource "aws_api_gateway_resource" "tests" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  parent_id   = aws_api_gateway_rest_api.main.root_resource_id
  path_part   = "tests"
}

resource "aws_api_gateway_resource" "test_by_id" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  parent_id   = aws_api_gateway_resource.tests.id
  path_part   = "{id}"
}

resource "aws_api_gateway_resource" "test_run" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  parent_id   = aws_api_gateway_resource.tests.id
  path_part   = "run"
}

resource "aws_api_gateway_resource" "test_generate" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  parent_id   = aws_api_gateway_resource.tests.id
  path_part   = "generate"
}

resource "aws_api_gateway_resource" "health" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  parent_id   = aws_api_gateway_rest_api.main.root_resource_id
  path_part   = "health"
}

# Methods - POST /tests/run
resource "aws_api_gateway_method" "post_test_run" {
  rest_api_id   = aws_api_gateway_rest_api.main.id
  resource_id   = aws_api_gateway_resource.test_run.id
  http_method   = "POST"
  authorization = var.enable_api_key ? "API_KEY" : "NONE"
  api_key_required = var.enable_api_key
}

resource "aws_api_gateway_integration" "post_test_run" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  resource_id = aws_api_gateway_resource.test_run.id
  http_method = aws_api_gateway_method.post_test_run.http_method
  
  integration_http_method = "POST"
  type                   = "AWS_PROXY"
  uri                    = aws_lambda_function.api_handler.invoke_arn
}

# Methods - GET /tests
resource "aws_api_gateway_method" "get_tests" {
  rest_api_id   = aws_api_gateway_rest_api.main.id
  resource_id   = aws_api_gateway_resource.tests.id
  http_method   = "GET"
  authorization = var.enable_api_key ? "API_KEY" : "NONE"
  api_key_required = var.enable_api_key
}

resource "aws_api_gateway_integration" "get_tests" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  resource_id = aws_api_gateway_resource.tests.id
  http_method = aws_api_gateway_method.get_tests.http_method
  
  integration_http_method = "POST"
  type                   = "AWS_PROXY"
  uri                    = aws_lambda_function.api_handler.invoke_arn
}

# Methods - GET /tests/{id}
resource "aws_api_gateway_method" "get_test_by_id" {
  rest_api_id   = aws_api_gateway_rest_api.main.id
  resource_id   = aws_api_gateway_resource.test_by_id.id
  http_method   = "GET"
  authorization = var.enable_api_key ? "API_KEY" : "NONE"
  api_key_required = var.enable_api_key
}

resource "aws_api_gateway_integration" "get_test_by_id" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  resource_id = aws_api_gateway_resource.test_by_id.id
  http_method = aws_api_gateway_method.get_test_by_id.http_method
  
  integration_http_method = "POST"
  type                   = "AWS_PROXY"
  uri                    = aws_lambda_function.api_handler.invoke_arn
}

# Methods - DELETE /tests/{id}
resource "aws_api_gateway_method" "delete_test" {
  rest_api_id   = aws_api_gateway_rest_api.main.id
  resource_id   = aws_api_gateway_resource.test_by_id.id
  http_method   = "DELETE"
  authorization = var.enable_api_key ? "API_KEY" : "NONE"
  api_key_required = var.enable_api_key
}

resource "aws_api_gateway_integration" "delete_test" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  resource_id = aws_api_gateway_resource.test_by_id.id
  http_method = aws_api_gateway_method.delete_test.http_method
  
  integration_http_method = "POST"
  type                   = "AWS_PROXY"
  uri                    = aws_lambda_function.api_handler.invoke_arn
}

# Methods - POST /tests/generate
resource "aws_api_gateway_method" "post_test_generate" {
  rest_api_id   = aws_api_gateway_rest_api.main.id
  resource_id   = aws_api_gateway_resource.test_generate.id
  http_method   = "POST"
  authorization = var.enable_api_key ? "API_KEY" : "NONE"
  api_key_required = var.enable_api_key
}

resource "aws_api_gateway_integration" "post_test_generate" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  resource_id = aws_api_gateway_resource.test_generate.id
  http_method = aws_api_gateway_method.post_test_generate.http_method
  
  integration_http_method = "POST"
  type                   = "AWS_PROXY"
  uri                    = aws_lambda_function.api_handler.invoke_arn
}

# Methods - GET /health
resource "aws_api_gateway_method" "get_health" {
  rest_api_id   = aws_api_gateway_rest_api.main.id
  resource_id   = aws_api_gateway_resource.health.id
  http_method   = "GET"
  authorization = "NONE"
  api_key_required = false
}

resource "aws_api_gateway_integration" "get_health" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  resource_id = aws_api_gateway_resource.health.id
  http_method = aws_api_gateway_method.get_health.http_method
  
  integration_http_method = "POST"
  type                   = "AWS_PROXY"
  uri                    = aws_lambda_function.api_handler.invoke_arn
}

# API Deployment
resource "aws_api_gateway_deployment" "main" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  
  triggers = {
    redeployment = sha1(jsonencode([
      aws_api_gateway_resource.tests.id,
      aws_api_gateway_method.post_test_run.id,
      aws_api_gateway_integration.post_test_run.id,
      aws_api_gateway_method.get_tests.id,
      aws_api_gateway_integration.get_tests.id,
      aws_api_gateway_method.get_test_by_id.id,
      aws_api_gateway_integration.get_test_by_id.id,
    ]))
  }
  
  lifecycle {
    create_before_destroy = true
  }
}

# API Stage
resource "aws_api_gateway_stage" "prod" {
  deployment_id = aws_api_gateway_deployment.main.id
  rest_api_id   = aws_api_gateway_rest_api.main.id
  stage_name    = "prod"
  
  xray_tracing_enabled = var.enable_xray
  
  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.api_gateway_logs.arn
    format = jsonencode({
      requestId      = "$context.requestId"
      ip             = "$context.identity.sourceIp"
      caller         = "$context.identity.caller"
      user           = "$context.identity.user"
      requestTime    = "$context.requestTime"
      httpMethod     = "$context.httpMethod"
      resourcePath   = "$context.resourcePath"
      status         = "$context.status"
      protocol       = "$context.protocol"
      responseLength = "$context.responseLength"
    })
  }
}

# CloudWatch Log Group for API Gateway
resource "aws_cloudwatch_log_group" "api_gateway_logs" {
  name              = "/aws/apigateway/${local.prefix}"
  retention_in_days = var.log_retention_days
}

# API Gateway Account (for CloudWatch logging)
resource "aws_api_gateway_account" "main" {
  cloudwatch_role_arn = aws_iam_role.api_gateway_cloudwatch.arn
}

# API Usage Plan
resource "aws_api_gateway_usage_plan" "main" {
  name = "${local.prefix}-usage-plan"
  
  api_stages {
    api_id = aws_api_gateway_rest_api.main.id
    stage  = aws_api_gateway_stage.prod.stage_name
  }
  
  throttle_settings {
    rate_limit  = var.api_rate_limit
    burst_limit = var.api_burst_limit
  }
  
  quota_settings {
    limit  = 10000
    period = "DAY"
  }
}

# API Key (if enabled)
resource "aws_api_gateway_api_key" "main" {
  count = var.enable_api_key ? 1 : 0
  name  = "${local.prefix}-api-key"
}

# API Key Usage Plan Association
resource "aws_api_gateway_usage_plan_key" "main" {
  count         = var.enable_api_key ? 1 : 0
  key_id        = aws_api_gateway_api_key.main[0].id
  key_type      = "API_KEY"
  usage_plan_id = aws_api_gateway_usage_plan.main.id
}

# Method settings for monitoring
resource "aws_api_gateway_method_settings" "all" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  stage_name  = aws_api_gateway_stage.prod.stage_name
  method_path = "*/*"
  
  settings {
    metrics_enabled    = true
    logging_level      = "INFO"
    data_trace_enabled = true
  }
}