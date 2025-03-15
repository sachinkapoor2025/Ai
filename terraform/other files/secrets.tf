# AWS Secrets Manager for API Keys
resource "aws_secretsmanager_secret" "forex_bot_secrets" {
  name = "ForexBotSecrets"
}

resource "aws_secretsmanager_secret_version" "forex_bot_secrets_version" {
  secret_id     = aws_secretsmanager_secret.forex_bot_secrets.id
  secret_string = jsonencode({
    OANDA_API_KEY = "your_oanda_api_key"
  })
}
