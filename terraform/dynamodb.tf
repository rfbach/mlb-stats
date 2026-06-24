resource "aws_dynamodb_table" "cubs_alerts" {
  name           = var.dynamodb_table_name
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "game_id"
  range_key      = "inning"

  attribute {
    name = "game_id"
    type = "N"
  }

  attribute {
    name = "inning"
    type = "N"
  }

  ttl {
    attribute_name = "ttl"
    enabled        = true
  }

  point_in_time_recovery {
    enabled = true
  }

  tags = {
    Name = var.dynamodb_table_name
  }
}

output "dynamodb_table_name" {
  description = "Name of the DynamoDB table"
  value       = aws_dynamodb_table.cubs_alerts.name
}

output "dynamodb_table_arn" {
  description = "ARN of the DynamoDB table"
  value       = aws_dynamodb_table.cubs_alerts.arn
}
