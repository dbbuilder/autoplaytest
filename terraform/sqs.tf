# SQS queue for test execution
resource "aws_sqs_queue" "test_queue" {
  name                      = "${local.prefix}-test-queue"
  delay_seconds             = 0
  max_message_size          = 262144
  message_retention_seconds = 1209600 # 14 days
  receive_wait_time_seconds = 20      # Long polling
  
  visibility_timeout_seconds = var.lambda_timeout + 60 # Lambda timeout + buffer
  
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.dlq.arn
    maxReceiveCount     = 3
  })
  
  tags = {
    Name = "${local.prefix}-test-queue"
  }
}

# SQS queue for result processing
resource "aws_sqs_queue" "result_queue" {
  name                      = "${local.prefix}-result-queue"
  delay_seconds             = 0
  max_message_size          = 262144
  message_retention_seconds = 86400 # 1 day
  receive_wait_time_seconds = 20
  
  visibility_timeout_seconds = 300
  
  tags = {
    Name = "${local.prefix}-result-queue"
  }
}

# Dead Letter Queue
resource "aws_sqs_queue" "dlq" {
  name                      = "${local.prefix}-dlq"
  message_retention_seconds = 1209600 # 14 days
  
  tags = {
    Name = "${local.prefix}-dlq"
  }
}

# SQS queue policy for S3 notifications
resource "aws_sqs_queue_policy" "s3_to_sqs" {
  queue_url = aws_sqs_queue.result_queue.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "s3.amazonaws.com"
        }
        Action   = "sqs:SendMessage"
        Resource = aws_sqs_queue.result_queue.arn
        Condition = {
          ArnEquals = {
            "aws:SourceArn" = aws_s3_bucket.results.arn
          }
        }
      }
    ]
  })
}

# CloudWatch alarms for DLQ
resource "aws_cloudwatch_metric_alarm" "dlq_messages" {
  alarm_name          = "${local.prefix}-dlq-messages"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "ApproximateNumberOfMessagesVisible"
  namespace           = "AWS/SQS"
  period              = "300"
  statistic           = "Average"
  threshold           = "0"
  alarm_description   = "This metric monitors DLQ messages"
  
  dimensions = {
    QueueName = aws_sqs_queue.dlq.name
  }
  
  alarm_actions = var.alarm_email != "" ? [aws_sns_topic.alerts.arn] : []
}