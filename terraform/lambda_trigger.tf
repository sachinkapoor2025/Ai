# Create a CloudWatch Event Rule to trigger Lambda every 4 hours
resource "aws_cloudwatch_event_rule" "lambda_schedule" {
  name                = "ai-fx-bot-schedule"
  description         = "Trigger Lambda function every 4 hours"
  schedule_expression = "rate(4 hours)"  # ✅ Runs every 4 hours
}

# Define CloudWatch Event Target (Lambda Function)
resource "aws_cloudwatch_event_target" "lambda_target" {
  rule      = aws_cloudwatch_event_rule.lambda_schedule.name
  target_id = "ai-fx-bot-target"
  arn       = aws_lambda_function.ai_fx_bot.arn
}

# Grant CloudWatch permission to invoke Lambda
resource "aws_lambda_permission" "allow_cloudwatch" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.ai_fx_bot.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.lambda_schedule.arn
}
