output "api_endpoint" {
  description = "API Gateway endpoint URL"
  value       = "${aws_api_gateway_stage.prod.invoke_url}"
}

output "api_key" {
  description = "API key for accessing the API (if enabled)"
  value       = var.enable_api_key ? aws_api_gateway_api_key.main[0].value : null
  sensitive   = true
}

output "lambda_function_names" {
  description = "Names of the Lambda functions"
  value = {
    test_executor     = aws_lambda_function.test_executor.function_name
    api_handler       = aws_lambda_function.api_handler.function_name
    result_processor  = aws_lambda_function.result_processor.function_name
  }
}

output "s3_buckets" {
  description = "S3 bucket names"
  value = {
    results           = aws_s3_bucket.results.id
    lambda_deployments = aws_s3_bucket.lambda_deployments.id
  }
}

output "dynamodb_tables" {
  description = "DynamoDB table names"
  value = {
    tasks         = aws_dynamodb_table.tasks.name
    test_results  = aws_dynamodb_table.test_results.name
  }
}

output "sqs_queues" {
  description = "SQS queue URLs"
  value = {
    test_queue    = aws_sqs_queue.test_queue.url
    result_queue  = aws_sqs_queue.result_queue.url
    dlq           = aws_sqs_queue.dlq.url
  }
}

output "secrets" {
  description = "Secrets Manager secret ARNs"
  value = {
    anthropic_api_key = aws_secretsmanager_secret.anthropic_api_key.arn
    openai_api_key    = aws_secretsmanager_secret.openai_api_key.arn
    google_api_key    = aws_secretsmanager_secret.google_api_key.arn
  }
}

output "cloudwatch_dashboard" {
  description = "CloudWatch dashboard URL"
  value       = "https://console.aws.amazon.com/cloudwatch/home?region=${var.region}#dashboards:name=${aws_cloudwatch_dashboard.main.dashboard_name}"
}

output "api_usage_plan_id" {
  description = "API Gateway usage plan ID"
  value       = aws_api_gateway_usage_plan.main.id
}

output "vpc_id" {
  description = "VPC ID (if VPC is enabled)"
  value       = var.enable_vpc ? aws_vpc.main[0].id : null
}

output "api_endpoints_detail" {
  description = "Detailed API endpoints"
  value = {
    health        = "${aws_api_gateway_stage.prod.invoke_url}/health"
    run_tests     = "${aws_api_gateway_stage.prod.invoke_url}/tests/run"
    generate_tests = "${aws_api_gateway_stage.prod.invoke_url}/tests/generate"
    get_test      = "${aws_api_gateway_stage.prod.invoke_url}/tests/{id}"
    list_tests    = "${aws_api_gateway_stage.prod.invoke_url}/tests"
  }
}

output "deployment_info" {
  description = "Deployment information"
  value = {
    project_name = var.project_name
    environment  = var.environment
    region       = var.region
    account_id   = local.account_id
    deployed_at  = timestamp()
  }
}