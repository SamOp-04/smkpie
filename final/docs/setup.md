# Deployment Guide

## Requirements
- Kubernetes Cluster (EKS recommended)
- Redis 6+
- Supabase Project

## Installation
1. Clone repository
2. Configure `.env` file
3. Deploy infrastructure:
```bash
terraform apply -var-file=prod.tfvars
kubectl apply -f infrastructure/k8s/