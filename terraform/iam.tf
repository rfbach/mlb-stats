resource "aws_iam_role" "lambda_role" {
  name = "cubs-strikeout-alerts-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

# Basic Lambda execution policy
resource "aws_iam_role_policy_attachment" "lambda_basic_execution" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# SES policy for sending emails
resource "aws_iam_role_policy" "lambda_ses_policy" {
  name = "cubs-strikeout-alerts-ses"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ses:SendEmail",
          "ses:SendRawEmail"
        ]
        Resource = "*"
      }
    ]
  })
}

# DynamoDB policy for state management
resource "aws_iam_role_policy" "lambda_dynamodb_policy" {
  name = "cubs-strikeout-alerts-dynamodb"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:DeleteItem",
          "dynamodb:Query"
        ]
        Resource = aws_dynamodb_table.cubs_alerts.arn
      }
    ]
  })
}

# EventBridge policy for dynamic frequency updates
resource "aws_iam_role_policy" "lambda_eventbridge_policy" {
  name = "cubs-strikeout-alerts-eventbridge"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "events:PutRule",
          "events:ListTargetsByRule",
          "events:PutTargets"
        ]
        Resource = "arn:aws:events:${var.aws_region}:*:rule/cubs-alert-*"
      }
    ]
  })
}

output "lambda_role_arn" {
  description = "ARN of the Lambda execution role"
  value       = aws_iam_role.lambda_role.arn
}

# EventBridge role for CloudWatch Logs
resource "aws_iam_role" "eventbridge_logs_role" {
  name = "cubs-alerts-eventbridge-logs-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "events.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy" "eventbridge_logs_policy" {
  name = "cubs-alerts-eventbridge-logs"
  role = aws_iam_role.eventbridge_logs_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "${aws_cloudwatch_log_group.cubs_alerts_eventbridge_logs.arn}:*"
      }
    ]
  })
}

output "eventbridge_logs_role_arn" {
  description = "ARN of the EventBridge CloudWatch Logs role"
  value       = aws_iam_role.eventbridge_logs_role.arn
}
