# Lambda Layer for Playwright and dependencies
resource "aws_lambda_layer_version" "playwright" {
  filename            = "lambda-layer.zip"
  layer_name          = "${local.prefix}-playwright-layer"
  compatible_runtimes = ["python3.12"]
  description         = "Playwright and dependencies for AutoPlayTest"
  
  # This will be created by build script
  source_code_hash = filebase64sha256("lambda-layer.zip")
}

# Lambda function for test execution
resource "aws_lambda_function" "test_executor" {
  filename         = "lambda_functions/test_executor.zip"
  function_name    = "${local.prefix}-test-executor"
  role            = aws_iam_role.lambda_execution.arn
  handler         = "handler.execute_test"
  runtime         = "python3.12"
  memory_size     = var.lambda_memory_size
  timeout         = var.lambda_timeout
  
  layers = [aws_lambda_layer_version.playwright.arn]
  
  environment {
    variables = merge(local.lambda_env_vars, {
      ANTHROPIC_API_KEY = aws_secretsmanager_secret_version.anthropic_api_key.secret_string
      OPENAI_API_KEY    = aws_secretsmanager_secret_version.openai_api_key.secret_string
      GOOGLE_API_KEY    = aws_secretsmanager_secret_version.google_api_key.secret_string
    })
  }
  
  vpc_config {
    subnet_ids         = var.enable_vpc ? aws_subnet.private[*].id : []
    security_group_ids = var.enable_vpc ? [aws_security_group.lambda.id] : []
  }
  
  tracing_config {
    mode = var.enable_xray ? "Active" : "PassThrough"
  }
  
  reserved_concurrent_executions = var.lambda_reserved_concurrent_executions
  
  dead_letter_config {
    target_arn = var.enable_dead_letter_queue ? aws_sqs_queue.dlq.arn : ""
  }
  
  depends_on = [
    aws_iam_role_policy_attachment.lambda_basic,
    aws_cloudwatch_log_group.lambda_logs
  ]
}

# Lambda function for API handling
resource "aws_lambda_function" "api_handler" {
  filename         = "lambda_functions/api_handler.zip"
  function_name    = "${local.prefix}-api-handler"
  role            = aws_iam_role.lambda_execution.arn
  handler         = "handler.handle_api"
  runtime         = "python3.12"
  memory_size     = 1024
  timeout         = 30
  
  environment {
    variables = merge(local.lambda_env_vars, {
      TEST_EXECUTOR_FUNCTION = aws_lambda_function.test_executor.function_name
    })
  }
  
  tracing_config {
    mode = var.enable_xray ? "Active" : "PassThrough"
  }
  
  depends_on = [
    aws_iam_role_policy_attachment.lambda_basic,
    aws_cloudwatch_log_group.api_logs
  ]
}

# Lambda function for result processing
resource "aws_lambda_function" "result_processor" {
  filename         = "lambda_functions/result_processor.zip"
  function_name    = "${local.prefix}-result-processor"
  role            = aws_iam_role.lambda_execution.arn
  handler         = "handler.process_results"
  runtime         = "python3.12"
  memory_size     = 512
  timeout         = 60
  
  environment {
    variables = local.lambda_env_vars
  }
  
  tracing_config {
    mode = var.enable_xray ? "Active" : "PassThrough"
  }
  
  depends_on = [
    aws_iam_role_policy_attachment.lambda_basic,
    aws_cloudwatch_log_group.processor_logs
  ]
}

# SQS trigger for result processor
resource "aws_lambda_event_source_mapping" "sqs_to_processor" {
  event_source_arn = aws_sqs_queue.result_queue.arn
  function_name    = aws_lambda_function.result_processor.arn
  batch_size       = 10
}

# CloudWatch Log Groups
resource "aws_cloudwatch_log_group" "lambda_logs" {
  name              = "/aws/lambda/${local.prefix}-test-executor"
  retention_in_days = var.log_retention_days
}

resource "aws_cloudwatch_log_group" "api_logs" {
  name              = "/aws/lambda/${local.prefix}-api-handler"
  retention_in_days = var.log_retention_days
}

resource "aws_cloudwatch_log_group" "processor_logs" {
  name              = "/aws/lambda/${local.prefix}-result-processor"
  retention_in_days = var.log_retention_days
}

# Lambda Permissions for API Gateway
resource "aws_lambda_permission" "api_gateway" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.api_handler.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.main.execution_arn}/*/*"
}

# Lambda Permissions for internal invocation
resource "aws_lambda_permission" "allow_api_to_executor" {
  statement_id  = "AllowInternalInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.test_executor.function_name
  principal     = aws_iam_role.lambda_execution.arn
}