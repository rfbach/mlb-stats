# Cubs Strikeout Alert Tool

A Python tool that monitors Chicago Cubs home games and sends email alerts whenever the Cubs pitchers achieve 3 strikeouts in an inning. Deployed on AWS Lambda with SES for notifications and DynamoDB for state tracking.

## Features

- ⚾ Monitors Cubs home games in real-time
- 🔔 Sends email alerts when Cubs pitchers get 3 strikeouts in an inning
- ☁️ Runs on AWS Lambda (serverless, cost-effective)
- 📧 Uses AWS SES for email delivery
- 💾 Tracks alert history with DynamoDB
- 🐍 Built with Python 3.10+

## Project Structure

```
src/
├── __init__.py           # Package initialization
├── config.py             # Configuration and constants
├── game_monitor.py       # Fetch and monitor Cubs home games
├── play_by_play.py       # Parse strikeout data from games
├── alerts.py             # Send email alerts via AWS SES
├── state.py              # DynamoDB state management
└── lambda_handler.py     # AWS Lambda entry point

test_local.py            # Local testing script
.env.example             # Environment variables template
pyproject.toml           # Poetry project configuration
```

## Setup Instructions

### 1. Install Dependencies

```bash
# Install project dependencies
poetry install

# Or with pip
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:
- `AWS_REGION`: Your AWS region (default: us-east-1)
- `SES_SENDER_EMAIL`: Verified SES sender email address
- `SES_RECIPIENT_EMAIL`: Email address to receive alerts
- `DYNAMODB_TABLE_NAME`: DynamoDB table name (default: cubs-alerts)

### 3. AWS Setup

#### Set up SES (Simple Email Service)

1. Go to AWS SES console
2. Verify your sender email address (it will send you a confirmation link)
3. Verify your recipient email address as well (for sandbox mode)
4. Request production access if you want to send to unverified addresses
5. Note the verified email addresses for `.env`

#### Set up AWS Credentials

Ensure you have AWS credentials configured:
- Via AWS CLI: `aws configure`
- Via environment variables: `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`
- Via IAM role (automatically available when running on Lambda)

#### Required IAM Permissions

Your Lambda execution role needs these permissions:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ses:SendEmail",
                "ses:SendRawEmail"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "dynamodb:GetItem",
                "dynamodb:PutItem",
                "dynamodb:DeleteItem",
                "dynamodb:Query"
            ],
            "Resource": "arn:aws:dynamodb:*:*:table/cubs-alerts"
        }
    ]
}
```

**For dynamic polling frequency (EventBridge management)**, add:
```json
{
    "Effect": "Allow",
    "Action": [
        "events:PutRule",
        "events:ListTargetsByRule",
        "events:PutTargets"
    ],
    "Resource": "arn:aws:events:*:*:rule/cubs-alert-*"
}
```

### 4. EventBridge Setup (For Dynamic Polling)

The system uses EventBridge rules that automatically adjust polling frequency based on game state:

**Rule 1: Frequent Polling (during games)**
- Initial schedule: `rate(30 minutes)` 
- Name: Set in `EVENTBRIDGE_RULE_NAME` env var (default: `cubs-alert-frequent`)
- Target: Your Lambda function
- **Automatically adjusts to:**
  - `rate(1 minute)` when games go live
  - `rate(60 minutes)` when all games finish

**Create this rule in AWS EventBridge console:**

1. Go to EventBridge → Rules
2. Create rule named `cubs-alert-frequent`
3. Schedule pattern: `rate(30 minutes)`
4. Target: Select your Lambda function
5. Click "Create"

**Optional: Rule 2: Daily Check (no-game days)**
- Schedule: `cron(0 2 * * ? *)` (2 AM daily)
- Name: `cubs-alert-minimal`
- Target: Your Lambda function
- Enabled initially (can be managed by separate scheduler Lambda)

### How Dynamic Polling Works

1. **Before games**: Polls every 30 minutes (low frequency to save costs)
2. **Game goes live**: Lambda detects state change → updates EventBridge → switches to 1-minute polling
3. **During game**: Catches strikeouts within 1 minute
4. **Game ends**: Lambda detects all games final → updates EventBridge → switches to 60-minute polling
5. **Next day**: Resets based on next day's schedule

**Cost impact:**
- Without optimization: ~105K invocations/year
- With dynamic polling: ~11K invocations/year (~90% savings!)

### 5. Local Testing

Test locally before deploying:

```bash
# Test game monitoring and play-by-play
python test_local.py
```

This will:
- Show today's Cubs home games
- Display current game status
- Show strikeout counts by inning (if game is live)

## Deployment to AWS Lambda

### Using AWS SAM (Recommended)

See `deployment/` directory for SAM template and deployment instructions.

### Manual Deployment

1. **Package your code**:
```bash
# Create deployment package
mkdir package
pip install -r requirements.txt -t package/
cp -r src/* package/

# Create zip file
cd package
zip -r ../lambda-function.zip .
cd ..
```

2. **Upload to Lambda**:
   - Go to AWS Lambda console
   - Create new function (Python 3.10 runtime)
   - Upload `lambda-function.zip`
   - Set handler to: `src.lambda_handler.lambda_handler`

3. **Configure environment variables** in Lambda console:
   - All variables from step 2 (.env)
   - `EVENTBRIDGE_RULE_NAME`: `cubs-alert-frequent` (or your custom name)

4. **Set Lambda execution role** with IAM permissions from step 3 (including EventBridge permissions)

5. **Create EventBridge rule** (see step 4 above)

## Usage

### Automatic (Lambda)

The Lambda function runs automatically on the EventBridge schedule and:
1. Checks for Cubs home games today
2. Monitors current inning strikeout count
3. Sends email alerts when 3 strikeouts are reached per inning
4. Tracks alerts in DynamoDB to avoid duplicates

### Manual Invocation

Trigger the Lambda manually for testing:

```bash
aws lambda invoke \
  --function-name cubs-strikeout-alerts \
  --payload '{}' \
  response.json
```

For manual testing with specific game data:

```bash
aws lambda invoke \
  --function-name cubs-strikeout-alerts \
  --payload '{"game_id": 119009, "inning": 3, "strikeout_count": 3}' \
  response.json
```

## Configuration Reference

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `AWS_REGION` | us-east-1 | AWS region |
| `SES_SENDER_EMAIL` | - | **Required** - Verified SES sender |
| `SES_RECIPIENT_EMAIL` | - | **Required** - Alert recipient |
| `DYNAMODB_TABLE_NAME` | cubs-alerts | DynamoDB state table |

### Constants (in `src/config.py`)

- `CUBS_TEAM_ID`: 112 (MLB team ID)
- `STRIKEOUTS_PER_INNING`: 3 (threshold for alerts)

## Development

### Run Tests

```bash
# Local testing
python test_local.py

# Run with specific game ID
python -c "from src.play_by_play import *; print(count_strikeouts_by_inning(119009))"
```

### Add New Features

1. Create functions in appropriate modules:
   - Game logic → `game_monitor.py`
   - Strikeout parsing → `play_by_play.py`
   - Notifications → `alerts.py`
   - State management → `state.py`

2. Update `lambda_handler.py` to use new functionality

3. Test locally with `test_local.py`

4. Deploy to AWS Lambda

## Troubleshooting

### No alerts being sent

1. Check SES email is verified in AWS console
2. Verify environment variables are set in Lambda
3. Check CloudWatch Logs for Lambda errors
4. Test with manual invocation

### Game data not found

- Ensure game is scheduled for today
- Verify game is a Cubs home game
- Check MLB API availability

### DynamoDB errors

- Ensure table exists and region matches
- Check IAM permissions for DynamoDB access
- Verify table name in environment variables

## Cost Estimation

- **Lambda**: ~$0.20 per 1M requests (~$1-2/month for game season)
- **DynamoDB**: Free tier includes 25 write units/month
- **SES**: ~$0.10 per 1000 emails (~$1-2/season)
- **Total**: ~$3-5/month during baseball season

## License

GPL-3.0 (inherited from mlb-statsapi dependency)

## References

- [MLB-StatsAPI Wiki](https://github.com/toddrob99/MLB-StatsAPI/wiki)
- [AWS SES Documentation](https://docs.aws.amazon.com/ses/)
- [AWS Lambda Documentation](https://docs.aws.amazon.com/lambda/)
- [AWS DynamoDB Documentation](https://docs.aws.amazon.com/dynamodb/)
