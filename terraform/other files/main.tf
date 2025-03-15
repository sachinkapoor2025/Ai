terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.region
}

module "networking" {
  source = "./networking.tf"
}

module "ecs" {
  source = "./ecs.tf"
}

module "s3" {
  source = "./s3.tf"
}

module "dynamodb" {
  source = "./dynamodb.tf"
}

module "secrets" {
  source = "./secrets.tf"
}

module "iam" {
  source = "./iam.tf"
}

output "ecs_cluster_name" {
  value = module.ecs.ecs_cluster_name
}

output "s3_bucket_name" {
  value = module.s3.s3_bucket_name
}

output "dynamodb_table_name" {
  value = module.dynamodb.dynamodb_table_name
}
