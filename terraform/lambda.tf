data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "${path.root}/.terraform/lambda_build"
  output_path = "${path.root}/.terraform/lambda_function.zip"
  depends_on  = [null_resource.build_lambda_package]
}

resource "null_resource" "build_lambda_package" {
  triggers = {
    requirements_hash = filemd5("${path.root}/../requirements.txt")
    source_hash       = filemd5("${path.root}/../src/lambda_handler.py")
  }

  provisioner "local-exec" {
    command = "cd ${path.root} && python build_lambda_package.py"
  }
}

resource "aws_lambda_function" "cubs_alerts" {
  filename         = data.archive_file.lambda_zip.output_path
  function_name   = var.lambda_function_name
  role            = aws_iam_role.lambda_role.arn
  handler         = "src.lambda_handler.lambda_handler"
  runtime         = var.python_runtime
  timeout         = var.lambda_timeout
  memory_size     = var.lambda_memory_size
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  logging_config {
    log_group  = aws_cloudwatch_log_group.cubs_alerts_lambda_logs.name
    log_format = "JSON"
  }
  environment {
    variables = {
      DYNAMODB_TABLE_NAME  = aws_dynamodb_table.cubs_alerts.name
      SES_SENDER_EMAIL     = var.ses_sender_email
      SES_RECIPIENT_EMAIL  = var.ses_recipient_email
      EVENTBRIDGE_RULE_NAME = var.eventbridge_rule_name
    }
  }

  depends_on = [
    aws_cloudwatch_log_group.cubs_alerts_lambda_logs,
    aws_iam_role_policy_attachment.lambda_basic_execution,
    aws_iam_role_policy.lambda_ses_policy,
    aws_iam_role_policy.lambda_dynamodb_policy,
    aws_iam_role_policy.lambda_eventbridge_policy
  ]

  tags = {
    Name = var.lambda_function_name
  }
}

output "lambda_function_arn" {
  description = "ARN of the Lambda function"
  value       = aws_lambda_function.cubs_alerts.arn
}

output "lambda_function_name" {
  description = "Name of the Lambda function"
  value       = aws_lambda_function.cubs_alerts.function_name
}
