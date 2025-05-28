provider "aws" {
  region = var.aws_region
}

resource "aws_s3_bucket" "model_storage" {
  bucket = var.s3_bucket_name
  acl    = "private"
}

resource "aws_eks_cluster" "cyber_api" {
  name     = "cyber-api-cluster"
  role_arn = aws_iam_role.eks_cluster.arn
  # ... other config
}