terraform {
  backend "s3" {
    bucket  = "ai-botbro"
    key     = "terraform-backend/terraform.tfstate"
    region  = "ap-southeast-2"
    encrypt = true
  }
}

provider "aws" {
  region = "ap-southeast-2"
}
