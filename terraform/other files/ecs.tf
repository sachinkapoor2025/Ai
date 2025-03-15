# ECS Cluster
resource "aws_ecs_cluster" "forex_bot_cluster" {
  name = "forex-bot-cluster"
}

# ECS Task Definition
resource "aws_ecs_task_definition" "forex_bot_task" {
  family                   = "forex-bot-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  memory                   = "512"
  cpu                      = "256"
  execution_role_arn       = aws_iam_role.ecs_execution_role.arn
  task_role_arn            = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([
    {
      name      = "forex-bot"
      image     = "your-docker-image-url"
      essential = true
      environment = [
        { "name": "DYNAMODB_TABLE", "value": aws_dynamodb_table.forex_bot_data.name },
        { "name": "S3_BUCKET", "value": aws_s3_bucket.forex_bot_models.bucket }
      ]
    }
  ])
}

# ECS Service
resource "aws_ecs_service" "forex_bot_service" {
  name            = "forex-bot-service"
  cluster        = aws_ecs_cluster.forex_bot_cluster.id
  task_definition = aws_ecs_task_definition.forex_bot_task.arn
  launch_type    = "FARGATE"

  network_configuration {
    subnets = ["subnet-your-subnet-id"]
    security_groups = ["sg-your-security-group-id"]
    assign_public_ip = true
  }
}
