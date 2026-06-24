variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "lambda_function_name" {
  description = "Name of the Lambda function"
  type        = string
  default     = "cubs-strikeout-alerts"
}

variable "eventbridge_rule_name" {
  description = "Name of the EventBridge rule"
  type        = string
  default     = "cubs-alert-frequent"
}

variable "dynamodb_table_name" {
  description = "Name of the DynamoDB table for state"
  type        = string
  default     = "cubs-alerts"
}

variable "ses_sender_email" {
  description = "Verified SES sender email address"
  type        = string
  sensitive   = true
}

variable "ses_recipient_email" {
  description = "Email address to receive alerts"
  type        = string
  sensitive   = true
}

variable "lambda_timeout" {
  description = "Lambda function timeout in seconds"
  type        = number
  default     = 60
}

variable "lambda_memory_size" {
  description = "Lambda function memory in MB"
  type        = number
  default     = 256
}

variable "python_runtime" {
  description = "Python runtime for Lambda"
  type        = string
  default     = "python3.10"
}

variable "log_retention_days" {
  description = "CloudWatch Log retention period in days"
  type        = number
  default     = 14
}
