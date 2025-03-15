provider "aws" {
  region  = "ap-southeast-2"
  }

# IAM Role for Lambda  
resource "aws_iam_role" "lambda_execution_role" {
  name = "ai-fx-lambda_execution_role"
  
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
}

# Attach policies to Lambda role  
resource "aws_iam_role_policy_attachment" "lambda_basic_execution" {
  role       = aws_iam_role.lambda_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "lambda_ecr_access" {
  role       = aws_iam_role.lambda_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
}

# Lambda Function using Docker Image  
resource "aws_lambda_function" "ai_fx_bot" {
  function_name     = "ai-fx-bot"
  role             = aws_iam_role.lambda_execution_role.arn
  package_type     = "Image"
  image_uri        = "985539754737.dkr.ecr.ap-southeast-2.amazonaws.com/ai-fx:latest"
  timeout          = 900 # 15 minutes (max for Lambda)
  memory_size      = 512

  environment {
    variables = {
      OANDA_ACCOUNT_ID = "your-account-id"
      OANDA_ACCESS_TOKEN = "your-api-key"
      TRADE_INSTRUMENT = "EUR_USD" # Default instrument
    }
  }
}

output "lambda_function_name" {
  value = aws_lambda_function.ai_fx_bot.function_name
}