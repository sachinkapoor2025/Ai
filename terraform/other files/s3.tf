# S3 Bucket for Model Storage
resource "aws_s3_bucket" "forex_bot_models" {
  bucket = "forex-bot-models"
  versioning {
    enabled = true
  }
}
