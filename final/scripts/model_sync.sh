#!/bin/bash

AWS_BUCKET=$(grep S3_BUCKET .env | cut -d '=' -f2)
MODEL_DIR="ml/models/"

aws s3 sync $MODEL_DIR s3://$AWS_BUCKET/models/