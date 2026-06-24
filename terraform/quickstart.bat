@echo off
REM Quick start script for Terraform deployment (Windows)

setlocal enabledelayedexpansion

echo.
echo === Cubs Strikeout Alerts - Terraform Quick Start ===
echo.

REM Check prerequisites
echo Checking prerequisites...

where terraform >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo X Terraform not found. Please install from https://www.terraform.io/downloads.html
    exit /b 1
)

where aws >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo X AWS CLI not found. Please install from https://aws.amazon.com/cli/
    exit /b 1
)

REM Check AWS credentials
aws sts get-caller-identity >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo X AWS credentials not configured. Run 'aws configure'
    exit /b 1
)

echo ✓ Prerequisites check passed
echo.

REM Check if already initialized
if not exist ".terraform" (
    echo Initializing Terraform...
    call terraform init
    echo ✓ Terraform initialized
) else (
    echo ✓ Terraform already initialized
)

echo.

REM Check if tfvars exists
if not exist "terraform.tfvars" (
    echo X terraform.tfvars not found
    echo Please copy terraform.tfvars.example to terraform.tfvars and update with your values:
    echo   copy terraform.tfvars.example terraform.tfvars
    echo   Then edit terraform.tfvars with your email addresses
    exit /b 1
)

echo ✓ terraform.tfvars found
echo.

REM Get user confirmation
echo Ready to deploy? This will create:
echo   - 1 Lambda function
echo   - 1 DynamoDB table
echo   - 2 EventBridge rules
echo   - 1 IAM role with policies
echo.

set /p confirm="Continue? (yes/no): "

if /i not "%confirm%"=="yes" (
    echo Cancelled
    exit /b 0
)

echo.
echo Running terraform plan...
call terraform plan -out=tfplan

echo.
set /p apply_confirm="Apply plan? (yes/no): "

if /i not "%apply_confirm%"=="yes" (
    echo Cancelled
    del /q tfplan 2>nul
    exit /b 0
)

echo.
echo Applying configuration...
call terraform apply tfplan
del /q tfplan 2>nul

echo.
echo === Deployment Complete ===
echo.
echo Next steps:
echo 1. Check AWS Console to verify resources were created
echo 2. Test the Lambda function
echo 3. Monitor CloudWatch Logs during Cubs games
echo.
echo View outputs:
call terraform output summary

echo.
pause
