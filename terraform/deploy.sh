#!/bin/bash
#
# Deploy Lambda Function
# Builds the Lambda deployment package and updates the Lambda function code.
# Requires AWS CLI and Terraform to be installed and configured.
#

set -e

TERRAFORM_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$TERRAFORM_DIR")"
BUILD_SCRIPT="$TERRAFORM_DIR/build_lambda_package.py"
LAMBDA_ZIP="$TERRAFORM_DIR/.terraform/lambda_function.zip"

echo "Building Lambda deployment package..."
if ! python3 "$BUILD_SCRIPT"; then
    echo "Build failed"
    exit 1
fi

if [ ! -f "$LAMBDA_ZIP" ]; then
    echo "Lambda package not found at $LAMBDA_ZIP"
    exit 1
fi

echo "Build successful"

# Get Lambda function name from Terraform output
echo "Retrieving Lambda function name..."
FUNCTION_NAME=$(cd "$TERRAFORM_DIR" && terraform output -json summary 2>/dev/null | jq -r '.value.lambda_function.name' 2>/dev/null)

if [ -z "$FUNCTION_NAME" ] || [ "$FUNCTION_NAME" = "null" ]; then
    echo "Failed to get Lambda function name from Terraform output"
    echo "Make sure Terraform has been applied: cd $TERRAFORM_DIR && terraform apply"
    exit 1
fi

# Get AWS region
AWS_REGION=$(aws configure get region)
if [ -z "$AWS_REGION" ]; then
    AWS_REGION="us-east-1"
fi

echo "Updating Lambda function: $FUNCTION_NAME"
if ! aws lambda update-function-code \
    --function-name "$FUNCTION_NAME" \
    --zip-file "fileb://$LAMBDA_ZIP" \
    --region "$AWS_REGION" \
    --output json > /dev/null; then
    echo "Deployment failed"
    exit 1
fi

echo "Lambda function updated successfully!"
echo "Function Name: $FUNCTION_NAME"
echo "Region: $AWS_REGION"
