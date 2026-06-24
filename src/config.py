"""Configuration and constants for the Cubs strikeout alert tool."""
import os
from typing import Optional

# MLB Team IDs
CUBS_TEAM_ID = 112

# Strikeout detection threshold
STRIKEOUTS_PER_INNING = 3

# AWS Configuration
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

# SES Configuration
SES_SENDER_EMAIL = os.getenv("SES_SENDER_EMAIL", "")
SES_RECIPIENT_EMAIL = os.getenv("SES_RECIPIENT_EMAIL", "")

# DynamoDB Configuration
DYNAMODB_TABLE_NAME = os.getenv("DYNAMODB_TABLE_NAME", "cubs-alerts")

# Game status constants
GAME_STATUS_LIVE = "Live"
GAME_STATUS_SCHEDULED = "Scheduled"
GAME_STATUS_FINAL = "Final"

# EventBridge Configuration
EVENTBRIDGE_RULE_NAME = os.getenv("EVENTBRIDGE_RULE_NAME", "cubs-alert-frequent")


def get_config() -> dict:
    """Get all configuration values."""
    return {
        "cubs_team_id": CUBS_TEAM_ID,
        "strikeouts_threshold": STRIKEOUTS_PER_INNING,
        "aws_region": AWS_REGION,
        "ses_sender": SES_SENDER_EMAIL,
        "ses_recipient": SES_RECIPIENT_EMAIL,
        "dynamodb_table": DYNAMODB_TABLE_NAME,
    }
