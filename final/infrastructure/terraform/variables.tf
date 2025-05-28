variable "aws_region" {
  description = "AWS deployment region"
  default     = "us-east-1"
}

variable "s3_bucket_name" {
  description = "Name for model storage bucket"
  type        = string
}

variable "eks_cluster_name" {
  description = "Name for EKS cluster"
  default     = "cyber-api-cluster"
}