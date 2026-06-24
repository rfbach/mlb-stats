"""Alert notification module using AWS SES."""
import boto3
from typing import Optional
from .config import (
    AWS_REGION,
    SES_SENDER_EMAIL,
    SES_RECIPIENT_EMAIL
)


def send_strikeout_alert(
    game_id: int,
    inning: int,
    strikeout_count: int,
    recipient_email: Optional[str] = None
) -> bool:
    """
    Send an email alert for Cubs strikeouts via SES.
    
    Args:
        game_id: MLB game ID
        inning: Inning number
        strikeout_count: Number of strikeouts in the inning
        recipient_email: Optional override for recipient email
        
    Returns:
        True if email sent successfully, False otherwise.
    """
    sender = SES_SENDER_EMAIL
    recipient = recipient_email or SES_RECIPIENT_EMAIL
    
    if not sender or not recipient:
        print("Error: SES_SENDER_EMAIL and SES_RECIPIENT_EMAIL must be configured")
        return False
    
    subject = f"⚾ Cubs Alert: {strikeout_count} Strikeouts in Inning {inning}!"
    
    body_text = f"""
Cubs Strikeout Alert!

Game ID: {game_id}
Inning: {inning}
Strikeouts by Cubs pitcher: {strikeout_count}

Three strikeouts achieved! 🔥
""".strip()
    
    body_html = f"""
<html>
<head></head>
<body>
  <h2>⚾ Cubs Strikeout Alert!</h2>
  <p><strong>Game ID:</strong> {game_id}</p>
  <p><strong>Inning:</strong> {inning}</p>
  <p><strong>Strikeouts by Cubs pitcher:</strong> {strikeout_count}</p>
  <p>Three strikeouts achieved! 🔥</p>
</body>
</html>
""".strip()
    
    try:
        client = boto3.client("ses", region_name=AWS_REGION)
        
        response = client.send_email(
            Source=sender,
            Destination={"ToAddresses": [recipient]},
            Message={
                "Subject": {"Data": subject, "Charset": "UTF-8"},
                "Body": {
                    "Text": {"Data": body_text, "Charset": "UTF-8"},
                    "Html": {"Data": body_html, "Charset": "UTF-8"},
                },
            },
        )
        
        print(f"Email sent successfully. Message ID: {response['MessageId']}")
        return True
        
    except Exception as e:
        print(f"Error sending email via SES: {e}")
        return False


def send_test_alert() -> bool:
    """
    Send a test alert email to verify SES configuration.
    
    Returns:
        True if email sent successfully, False otherwise.
    """
    sender = SES_SENDER_EMAIL
    recipient = SES_RECIPIENT_EMAIL
    
    if not sender or not recipient:
        print("Error: SES_SENDER_EMAIL and SES_RECIPIENT_EMAIL must be configured")
        return False
    
    subject = "Test: Cubs Strikeout Alert System"
    
    body_text = """
This is a test email from the Cubs strikeout alert system.

If you received this, your SES configuration is working correctly!
""".strip()
    
    body_html = """
<html>
<head></head>
<body>
  <h2>Cubs Strikeout Alert System - Test Email</h2>
  <p>If you received this, your SES configuration is working correctly!</p>
</body>
</html>
""".strip()
    
    try:
        client = boto3.client("ses", region_name=AWS_REGION)
        
        response = client.send_email(
            Source=sender,
            Destination={"ToAddresses": [recipient]},
            Message={
                "Subject": {"Data": subject, "Charset": "UTF-8"},
                "Body": {
                    "Text": {"Data": body_text, "Charset": "UTF-8"},
                    "Html": {"Data": body_html, "Charset": "UTF-8"},
                },
            },
        )
        
        print(f"Test email sent successfully. Message ID: {response['MessageId']}")
        return True
        
    except Exception as e:
        print(f"Error sending test email: {e}")
        return False
