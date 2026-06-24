# CloudWatch Log Group for Lambda function
resource "aws_cloudwatch_log_group" "cubs_alerts_lambda_logs" {
  name              = "/aws/lambda/${var.lambda_function_name}"
  retention_in_days = var.log_retention_days

  tags = {
    Name = "${var.lambda_function_name}-logs"
  }
}

# CloudWatch Log Group for EventBridge rules
resource "aws_cloudwatch_log_group" "cubs_alerts_eventbridge_logs" {
  name              = "/aws/events/cubs-alerts"
  retention_in_days = var.log_retention_days

  tags = {
    Name = "cubs-alerts-eventbridge-logs"
  }
}

output "lambda_log_group_name" {
  description = "Name of the Lambda function CloudWatch Log Group"
  value       = aws_cloudwatch_log_group.cubs_alerts_lambda_logs.name
}

output "eventbridge_log_group_name" {
  description = "Name of the EventBridge CloudWatch Log Group"
  value       = aws_cloudwatch_log_group.cubs_alerts_eventbridge_logs.name
}
