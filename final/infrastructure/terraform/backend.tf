terraform {
  backend "s3" {
    bucket         = "cyber-api-tfstate"
    key            = "prod/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "tf-lock-table"
  }
}