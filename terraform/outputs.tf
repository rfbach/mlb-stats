output "summary" {
  description = "Summary of created resources"
  value = {
    lambda_function = {
      name = aws_lambda_function.cubs_alerts.function_name
      arn  = aws_lambda_function.cubs_alerts.arn
    }
    dynamodb_table = {
      name = aws_dynamodb_table.cubs_alerts.name
      arn  = aws_dynamodb_table.cubs_alerts.arn
    }
    eventbridge_rules = {
      frequent = {
        name = aws_cloudwatch_event_rule.cubs_alert_frequent.name
        arn  = aws_cloudwatch_event_rule.cubs_alert_frequent.arn
      }
      minimal = {
        name = aws_cloudwatch_event_rule.cubs_alert_minimal.name
        arn  = aws_cloudwatch_event_rule.cubs_alert_minimal.arn
      }
    }
    iam_role = {
      name = aws_iam_role.lambda_role.name
      arn  = aws_iam_role.lambda_role.arn
    }
  }
}
