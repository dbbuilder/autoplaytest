# Secrets Manager for API keys
resource "aws_secretsmanager_secret" "anthropic_api_key" {
  name                    = "${local.prefix}-anthropic-api-key"
  description             = "Anthropic API key for Claude AI provider"
  recovery_window_in_days = 7
  
  tags = {
    Name = "${local.prefix}-anthropic-api-key"
  }
}

resource "aws_secretsmanager_secret_version" "anthropic_api_key" {
  secret_id     = aws_secretsmanager_secret.anthropic_api_key.id
  secret_string = var.anthropic_api_key
}

resource "aws_secretsmanager_secret" "openai_api_key" {
  name                    = "${local.prefix}-openai-api-key"
  description             = "OpenAI API key for GPT provider"
  recovery_window_in_days = 7
  
  tags = {
    Name = "${local.prefix}-openai-api-key"
  }
}

resource "aws_secretsmanager_secret_version" "openai_api_key" {
  secret_id     = aws_secretsmanager_secret.openai_api_key.id
  secret_string = var.openai_api_key
}

resource "aws_secretsmanager_secret" "google_api_key" {
  name                    = "${local.prefix}-google-api-key"
  description             = "Google API key for Gemini provider"
  recovery_window_in_days = 7
  
  tags = {
    Name = "${local.prefix}-google-api-key"
  }
}

resource "aws_secretsmanager_secret_version" "google_api_key" {
  secret_id     = aws_secretsmanager_secret.google_api_key.id
  secret_string = var.google_api_key
}

# API Gateway API key secret (if enabled)
resource "aws_secretsmanager_secret" "api_gateway_key" {
  count                   = var.enable_api_key ? 1 : 0
  name                    = "${local.prefix}-api-gateway-key"
  description             = "API Gateway API key for AutoPlayTest"
  recovery_window_in_days = 7
  
  tags = {
    Name = "${local.prefix}-api-gateway-key"
  }
}

resource "aws_secretsmanager_secret_version" "api_gateway_key" {
  count         = var.enable_api_key ? 1 : 0
  secret_id     = aws_secretsmanager_secret.api_gateway_key[0].id
  secret_string = aws_api_gateway_api_key.main[0].value
}