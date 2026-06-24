resource "aws_cloudwatch_event_rule" "cubs_alert_frequent" {
  name                = var.eventbridge_rule_name
  description         = "Frequent polling for Cubs strikeout alerts during game days"
  schedule_expression = "rate(30 minutes)"
  state               = "ENABLED"

  tags = {
    Name = var.eventbridge_rule_name
  }
}

resource "aws_cloudwatch_event_target" "cubs_alert_frequent_lambda" {
  rule      = aws_cloudwatch_event_rule.cubs_alert_frequent.name
  target_id = "CubsStrikeoutAlertsLambda"
  arn       = aws_lambda_function.cubs_alerts.arn
}

resource "aws_cloudwatch_event_target" "cubs_alert_frequent_logs" {
  rule      = aws_cloudwatch_event_rule.cubs_alert_frequent.name
  target_id = "EventBridgeLogs"
  arn       = aws_cloudwatch_log_group.cubs_alerts_eventbridge_logs.arn
}

resource "aws_lambda_permission" "allow_eventbridge" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.cubs_alerts.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.cubs_alert_frequent.arn
}

# Optional: Daily minimal polling rule (for no-game days)
resource "aws_cloudwatch_event_rule" "cubs_alert_minimal" {
  name                = "cubs-alert-minimal"
  description         = "Minimal daily polling for Cubs strikeout alerts"
  schedule_expression = "cron(0 12 * * ? *)"
  state               = "DISABLED"  # Disabled by default, can be enabled by handler

  tags = {
    Name = "cubs-alert-minimal"
  }
}

resource "aws_cloudwatch_event_target" "cubs_alert_minimal_lambda" {
  rule      = aws_cloudwatch_event_rule.cubs_alert_minimal.name
  target_id = "CubsStrikeoutAlertsLambda"
  arn       = aws_lambda_function.cubs_alerts.arn
}

resource "aws_cloudwatch_event_target" "cubs_alert_minimal_logs" {
  rule      = aws_cloudwatch_event_rule.cubs_alert_minimal.name
  target_id = "EventBridgeLogs"
  arn       = aws_cloudwatch_log_group.cubs_alerts_eventbridge_logs.arn
}

resource "aws_lambda_permission" "allow_eventbridge_minimal" {
  statement_id  = "AllowExecutionFromEventBridgeMinimal"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.cubs_alerts.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.cubs_alert_minimal.arn
}

output "eventbridge_rule_arn" {
  description = "ARN of the frequent polling EventBridge rule"
  value       = aws_cloudwatch_event_rule.cubs_alert_frequent.arn
}

output "eventbridge_rule_name" {
  description = "Name of the frequent polling EventBridge rule"
  value       = aws_cloudwatch_event_rule.cubs_alert_frequent.name
}
