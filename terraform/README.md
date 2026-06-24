# Terraform Deployment - Cubs Strikeout Alerts

This directory contains Terraform configuration to deploy the Cubs strikeout alert system on AWS.

## Prerequisites

1. **Terraform** >= 1.0
   ```bash
   # Install from https://www.terraform.io/downloads.html
   # Or via package manager:
   # macOS: brew install terraform
   # Windows: choco install terraform
   # Linux: Check your package manager
   ```

2. **AWS CLI** configured with credentials
   ```bash
   aws configure
   # Enter your Access Key ID, Secret Access Key, region, and output format
   ```

3. **Verified SES Email Addresses**
   - Go to AWS SES console
   - Verify your sender email address (will receive confirmation link)
   - Verify your recipient email address (required for sandbox mode)
   - Request production access if sending to unverified addresses

## Files Overview

- `provider.tf` - AWS provider and backend configuration
- `variables.tf` - Input variables with descriptions
- `iam.tf` - IAM roles and policies for Lambda
- `lambda.tf` - Lambda function definition
- `dynamodb.tf` - DynamoDB table for state tracking
- `eventbridge.tf` - EventBridge rules for scheduling
- `outputs.tf` - Output values after deployment
- `terraform.tfvars.example` - Example variable values

## Deployment Steps

### 1. Prepare Variables

```bash
cd terraform

# Copy example variables file
cp terraform.tfvars.example terraform.tfvars

# Edit with your values
nano terraform.tfvars  # or use your editor
```

**Required updates in `terraform.tfvars`:**
```hcl
aws_region              = "us-east-1"              # Your AWS region
ses_sender_email        = "alerts@example.com"     # Verified SES sender
ses_recipient_email     = "you@example.com"        # Recipient email
```

**Optional customizations:**
```hcl
environment             = "prod"                    # dev, staging, or prod
lambda_function_name    = "cubs-strikeout-alerts"
lambda_timeout          = 60                        # seconds
lambda_memory_size      = 256                       # MB
eventbridge_rule_name   = "cubs-alert-frequent"
dynamodb_table_name     = "cubs-alerts"
```

### 2. Initialize Terraform

```bash
terraform init
```

This downloads the AWS provider and prepares the working directory.

### 3. Plan Deployment

```bash
terraform plan
```

Review the planned changes. You should see:
- 1 Lambda function
- 1 DynamoDB table
- 2 EventBridge rules
- 1 IAM role
- 4 IAM policies
- 2 Lambda permissions

### 4. Apply Configuration

```bash
terraform apply
```

Review the plan output, then type `yes` when prompted to create resources.

```bash
# Alternative: approve without prompt
terraform apply -auto-approve
```

### 5. Verify Deployment

After deployment, you'll see outputs including:

```
Outputs:

summary = {
  "dynamodb_table" = {
    "arn" = "arn:aws:dynamodb:us-east-1:123456789:table/cubs-alerts"
    "name" = "cubs-alerts"
  }
  "eventbridge_rules" = {
    "frequent" = {
      "arn" = "arn:aws:events:us-east-1:123456789:rule/cubs-alert-frequent"
      "name" = "cubs-alert-frequent"
    }
    ...
  }
  ...
}
```

## Verify Resources in AWS Console

1. **Lambda**: `Services > Lambda > Functions > cubs-strikeout-alerts`
   - Check environment variables
   - Verify IAM role is attached

2. **DynamoDB**: `Services > DynamoDB > Tables > cubs-alerts`
   - Confirm table structure
   - Check TTL is enabled

3. **EventBridge**: `Services > EventBridge > Rules`
   - `cubs-alert-frequent`: Should be enabled with 30-minute schedule
   - `cubs-alert-minimal`: Disabled by default

4. **IAM**: `Services > IAM > Roles > cubs-strikeout-alerts-lambda-role`
   - Verify all 4 policies are attached

## Testing Lambda

```bash
# Test manually via AWS CLI
aws lambda invoke \
  --function-name cubs-strikeout-alerts \
  --region us-east-1 \
  response.json

cat response.json
```

## Managing State

### Local State (Development)

By default, Terraform stores state locally in `terraform.tfstate`. This is fine for development but not recommended for production.

### S3 Backend (Production)

Uncomment the backend configuration in `provider.tf`:

```hcl
backend "s3" {
  bucket         = "your-terraform-state-bucket"
  key            = "cubs-alerts/terraform.tfstate"
  region         = "us-east-1"
  encrypt        = true
  dynamodb_table = "terraform-lock"
}
```

Then:

```bash
terraform init
# Choose "yes" to migrate state to S3
```

## Updating Configuration

After making changes to `.tf` files:

```bash
terraform plan      # Review changes
terraform apply     # Apply changes
```

## Common Operations

### Update Lambda Environment Variables

Edit `variables.tf` or `terraform.tfvars`, then:

```bash
terraform apply
```

### Modify EventBridge Schedule

Edit the `schedule_expression` in `eventbridge.tf`:

```hcl
schedule_expression = "rate(15 minutes)"  # Changed from 30 minutes
```

Then apply:

```bash
terraform apply
```

### Destroy All Resources

**Warning**: This will delete everything including the DynamoDB table (with backups via PITR).

```bash
terraform destroy
```

## Troubleshooting

### Lambda Deployment Fails

**Error**: `Unable to create Lambda: ValidationException`

**Solution**: Ensure `src/` directory exists and has `lambda_handler.py`:

```bash
ls -la ../src/lambda_handler.py
```

### SES Email Fails

**Error**: `MessageRejected: Email address not verified`

**Solution**: Verify email in AWS SES console for your region

### EventBridge Rule Not Triggering

**Error**: Lambda not invoked at scheduled time

**Solution**: 
- Check CloudWatch Logs: `Services > CloudWatch > Log Groups > /aws/lambda/cubs-strikeout-alerts`
- Verify rule is ENABLED: `Services > EventBridge > Rules > cubs-alert-frequent`

## Cost Estimation

Monthly costs (approximate, US East 1):

| Service | Estimate |
|---------|----------|
| Lambda | ~$1-2 (11K invocations/month) |
| DynamoDB | ~$1 (pay-per-request) |
| EventBridge | Free (first 100K events) |
| SES | ~$0.10 (email alerts) |
| **Total** | **~$2-3/month** |

## Security Best Practices

1. ✅ Never commit `terraform.tfvars` (contains sensitive data)
2. ✅ Use AWS Secrets Manager for sensitive config (future enhancement)
3. ✅ Enable MFA for AWS root account
4. ✅ Use least-privilege IAM policies (done)
5. ✅ Enable DynamoDB point-in-time recovery (done)
6. ✅ Use S3 backend with encryption (recommended for production)

## Next Steps

1. ✅ Run `terraform init`
2. ✅ Prepare `terraform.tfvars` with your email addresses
3. ✅ Run `terraform plan` to review
4. ✅ Run `terraform apply` to deploy
5. ✅ Test Lambda via AWS Console or CLI
6. ✅ Monitor CloudWatch Logs during Cubs games

## Support

For issues with:
- **Terraform**: See [Terraform AWS Provider Docs](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- **Cubs Alerts**: See `../README.md`
- **AWS Services**: Check AWS documentation or support
