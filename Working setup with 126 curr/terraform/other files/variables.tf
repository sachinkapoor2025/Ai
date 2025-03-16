variable "region" {
  description = "AWS region"
  default     = "ap-southeast-2"
}

variable "subnet_id" {
  description = "Subnet ID for ECS"
  type        = string
}

variable "security_group_id" {
  description = "Security Group ID for ECS"
  type        = string
}

variable "docker_image_url" {
  description = "Docker image URL for ECS"
  type        = string
}
