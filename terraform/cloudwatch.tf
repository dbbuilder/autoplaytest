# SNS topic for alerts
resource "aws_sns_topic" "alerts" {
  name = "${local.prefix}-alerts"
  
  tags = {
    Name = "${local.prefix}-alerts"
  }
}

# SNS topic subscription
resource "aws_sns_topic_subscription" "alerts_email" {
  count     = var.alarm_email != "" ? 1 : 0
  topic_arn = aws_sns_topic.alerts.arn
  protocol  = "email"
  endpoint  = var.alarm_email
}

# CloudWatch Dashboard
resource "aws_cloudwatch_dashboard" "main" {
  dashboard_name = "${local.prefix}-dashboard"
  
  dashboard_body = jsonencode({
    widgets = [
      {
        type   = "metric"
        width  = 12
        height = 6
        properties = {
          metrics = [
            ["AWS/Lambda", "Invocations", { stat = "Sum" }],
            [".", "Errors", { stat = "Sum" }],
            [".", "Duration", { stat = "Average" }],
            [".", "ConcurrentExecutions", { stat = "Maximum" }]
          ]
          view    = "timeSeries"
          stacked = false
          region  = var.region
          title   = "Lambda Metrics"
          period  = 300
        }
      },
      {
        type   = "metric"
        width  = 12
        height = 6
        properties = {
          metrics = [
            ["AWS/ApiGateway", "Count", { stat = "Sum" }],
            [".", "4XXError", { stat = "Sum" }],
            [".", "5XXError", { stat = "Sum" }],
            [".", "Latency", { stat = "Average" }]
          ]
          view    = "timeSeries"
          stacked = false
          region  = var.region
          title   = "API Gateway Metrics"
          period  = 300
        }
      },
      {
        type   = "metric"
        width  = 12
        height = 6
        properties = {
          metrics = [
            ["AWS/DynamoDB", "UserErrors", { stat = "Sum" }],
            [".", "SystemErrors", { stat = "Sum" }],
            [".", "ConsumedReadCapacityUnits", { stat = "Sum" }],
            [".", "ConsumedWriteCapacityUnits", { stat = "Sum" }]
          ]
          view    = "timeSeries"
          stacked = false
          region  = var.region
          title   = "DynamoDB Metrics"
          period  = 300
        }
      },
      {
        type   = "metric"
        width  = 12
        height = 6
        properties = {
          metrics = [
            ["AWS/SQS", "NumberOfMessagesSent", { stat = "Sum" }],
            [".", "NumberOfMessagesReceived", { stat = "Sum" }],
            [".", "NumberOfMessagesDeleted", { stat = "Sum" }],
            [".", "ApproximateNumberOfMessagesVisible", { stat = "Maximum" }]
          ]
          view    = "timeSeries"
          stacked = false
          region  = var.region
          title   = "SQS Metrics"
          period  = 300
        }
      }
    ]
  })
}

# Lambda Error Alarm
resource "aws_cloudwatch_metric_alarm" "lambda_errors" {
  alarm_name          = "${local.prefix}-lambda-errors"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  period              = "300"
  statistic           = "Sum"
  threshold           = "10"
  alarm_description   = "This metric monitors Lambda errors"
  
  dimensions = {
    FunctionName = aws_lambda_function.test_executor.function_name
  }
  
  alarm_actions = var.alarm_email != "" ? [aws_sns_topic.alerts.arn] : []
}

# Lambda Duration Alarm
resource "aws_cloudwatch_metric_alarm" "lambda_duration" {
  alarm_name          = "${local.prefix}-lambda-duration"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "Duration"
  namespace           = "AWS/Lambda"
  period              = "300"
  statistic           = "Average"
  threshold           = "300000" # 5 minutes
  alarm_description   = "This metric monitors Lambda execution duration"
  
  dimensions = {
    FunctionName = aws_lambda_function.test_executor.function_name
  }
  
  alarm_actions = var.alarm_email != "" ? [aws_sns_topic.alerts.arn] : []
}

# API Gateway 4XX Errors
resource "aws_cloudwatch_metric_alarm" "api_4xx_errors" {
  alarm_name          = "${local.prefix}-api-4xx-errors"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "4XXError"
  namespace           = "AWS/ApiGateway"
  period              = "300"
  statistic           = "Sum"
  threshold           = "50"
  alarm_description   = "This metric monitors API Gateway 4XX errors"
  
  dimensions = {
    ApiName = aws_api_gateway_rest_api.main.name
    Stage   = aws_api_gateway_stage.prod.stage_name
  }
  
  alarm_actions = var.alarm_email != "" ? [aws_sns_topic.alerts.arn] : []
}

# API Gateway 5XX Errors
resource "aws_cloudwatch_metric_alarm" "api_5xx_errors" {
  alarm_name          = "${local.prefix}-api-5xx-errors"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "5XXError"
  namespace           = "AWS/ApiGateway"
  period              = "60"
  statistic           = "Sum"
  threshold           = "5"
  alarm_description   = "This metric monitors API Gateway 5XX errors"
  
  dimensions = {
    ApiName = aws_api_gateway_rest_api.main.name
    Stage   = aws_api_gateway_stage.prod.stage_name
  }
  
  alarm_actions = var.alarm_email != "" ? [aws_sns_topic.alerts.arn] : []
}

# DynamoDB Throttling
resource "aws_cloudwatch_metric_alarm" "dynamodb_throttles" {
  alarm_name          = "${local.prefix}-dynamodb-throttles"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "UserErrors"
  namespace           = "AWS/DynamoDB"
  period              = "300"
  statistic           = "Sum"
  threshold           = "10"
  alarm_description   = "This metric monitors DynamoDB throttling"
  
  dimensions = {
    TableName = aws_dynamodb_table.tasks.name
  }
  
  alarm_actions = var.alarm_email != "" ? [aws_sns_topic.alerts.arn] : []
}