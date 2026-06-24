#!/bin/bash
# Quick start script for Terraform deployment

set -e

echo "=== Cubs Strikeout Alerts - Terraform Quick Start ==="
echo ""

# Check prerequisites
echo "Checking prerequisites..."

if ! command -v terraform &> /dev/null; then
    echo "❌ Terraform not found. Please install from https://www.terraform.io/downloads.html"
    exit 1
fi

if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI not found. Please install from https://aws.amazon.com/cli/"
    exit 1
fi

# Check AWS credentials
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS credentials not configured. Run 'aws configure'"
    exit 1
fi

echo "✅ Prerequisites check passed"
echo ""

# Check if already initialized
if [ ! -d ".terraform" ]; then
    echo "Initializing Terraform..."
    terraform init
    echo "✅ Terraform initialized"
else
    echo "✅ Terraform already initialized"
fi

echo ""

# Check if tfvars exists
if [ ! -f "terraform.tfvars" ]; then
    echo "❌ terraform.tfvars not found"
    echo "Please copy terraform.tfvars.example to terraform.tfvars and update with your values:"
    echo "  cp terraform.tfvars.example terraform.tfvars"
    echo "  nano terraform.tfvars"
    exit 1
fi

echo "✅ terraform.tfvars found"
echo ""

# Get user confirmation
echo "Ready to deploy? This will create:"
echo "  - 1 Lambda function"
echo "  - 1 DynamoDB table"
echo "  - 2 EventBridge rules"
echo "  - 1 IAM role with policies"
echo ""

read -p "Continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Cancelled"
    exit 0
fi

echo ""
echo "Running terraform plan..."
terraform plan -out=tfplan

echo ""
read -p "Apply plan? (yes/no): " apply_confirm

if [ "$apply_confirm" != "yes" ]; then
    echo "Cancelled"
    rm -f tfplan
    exit 0
fi

echo ""
echo "Applying configuration..."
terraform apply tfplan
rm -f tfplan

echo ""
echo "=== Deployment Complete ==="
echo ""
echo "Next steps:"
echo "1. Check AWS Console to verify resources were created"
echo "2. Test the Lambda function"
echo "3. Monitor CloudWatch Logs during Cubs games"
echo ""
echo "View outputs:"
terraform output summary
