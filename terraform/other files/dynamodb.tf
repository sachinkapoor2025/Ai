# DynamoDB Table for Trading Data
resource "aws_dynamodb_table" "forex_bot_data" {
  name         = "ForexBotData"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "TradeID"

  attribute {
    name = "TradeID"
    type = "S"
  }
}
