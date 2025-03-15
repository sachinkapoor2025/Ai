output "ecs_cluster_name" {
  value = aws_ecs_cluster.forex_bot_cluster.name
}

output "s3_bucket_name" {
  value = aws_s3_bucket.forex_bot_models.id
}

output "dynamodb_table_name" {
  value = aws_dynamodb_table.forex_bot_data.id
}
