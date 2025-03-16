# VPC Creation
resource "aws_vpc" "forex_bot_vpc" {
  cidr_block = "10.0.0.0/16"
}

# Subnet Creation
resource "aws_subnet" "forex_bot_subnet" {
  vpc_id                  = aws_vpc.forex_bot_vpc.id
  cidr_block              = "10.0.1.0/24"
  map_public_ip_on_launch = true
}

# Security Group
resource "aws_security_group" "forex_bot_sg" {
  vpc_id = aws_vpc.forex_bot_vpc.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}