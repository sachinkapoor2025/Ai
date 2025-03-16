# Fetch the latest ECR image
data "aws_ecr_image" "latest_ai_fx_image" {
  repository_name = ai-fx
  most_recent     = true
}

# Lambda Function using Docker Image 
resource "aws_lambda_function" "ai_fx_bot" {
  function_name     = "ai-fx-bot"
  role             = aws_iam_role.lambda_execution_role.arn
  package_type     = "Image"

  # Use the latest image digest
  image_uri = "${data.aws_ecr_repository.existing_ai_fx.repository_url}@${data.aws_ecr_image.latest_ai_fx_image.image_digest}"

  timeout          = 900  # 15 minutes (max for Lambda)
  memory_size      = 1024 # Increased to 1GB for better performance

  environment {
    variables = {
      OANDA_ACCOUNT_ID = "your-account-id"
      OANDA_ACCESS_TOKEN = "your-api-key"
      TRADE_INSTRUMENT = "EUR_USD"
    }
  }
}

output "lambda_function_name" {
  value = aws_lambda_function.ai_fx_bot.function_name
}