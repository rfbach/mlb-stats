#Requires -Version 5.0
<#
.SYNOPSIS
Deploys updated Python code to AWS Lambda.

.DESCRIPTION
Builds the Lambda deployment package and updates the Lambda function code.
Requires AWS CLI to be configured with appropriate credentials.

.EXAMPLE
.\deploy.ps1
#>

$ErrorActionPreference = "Stop"

$TerraformDir = $PSScriptRoot
$ProjectRoot = Split-Path -Parent $TerraformDir
$BuildScript = Join-Path $TerraformDir "build_lambda_package.py"
$LambdaZip = Join-Path (Join-Path $TerraformDir ".terraform") "lambda_function.zip"

Write-Host "Building Lambda deployment package..." -ForegroundColor Cyan
try {
    & python $BuildScript
    if ($LASTEXITCODE -ne 0) {
        throw "Build script failed with exit code $LASTEXITCODE"
    }
} catch {
    Write-Host "Build failed: $_" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $LambdaZip)) {
    Write-Host "Lambda package not found at $LambdaZip" -ForegroundColor Red
    exit 1
}

Write-Host "Build successful" -ForegroundColor Green

# Get Lambda function name from Terraform output
Write-Host "Retrieving Lambda function name..." -ForegroundColor Cyan
try {
    Push-Location $TerraformDir
    $Output = & terraform output -json summary | ConvertFrom-Json
    Pop-Location
    
    $FunctionName = $Output.lambda_function.name
    
    if (-not $FunctionName) {
        throw "Could not extract function name from Terraform output"
    }
} catch {
    Write-Host "Failed to get Terraform output: $_" -ForegroundColor Red
    Write-Host "Make sure Terraform has been applied" -ForegroundColor Yellow
    exit 1
}

Write-Host "Updating Lambda function: $FunctionName" -ForegroundColor Cyan
try {
    $ZipBytes = [System.IO.File]::ReadAllBytes($LambdaZip)
    
    aws lambda update-function-code `
        --function-name $FunctionName `
        --zip-file "fileb://$LambdaZip" `
        --region (aws configure get region) `
        --output json | Out-Null
    
    if ($LASTEXITCODE -ne 0) {
        throw "AWS Lambda update failed with exit code $LASTEXITCODE"
    }
} catch {
    Write-Host "Deployment failed: $_" -ForegroundColor Red
    exit 1
}

Write-Host "Lambda function updated successfully!" -ForegroundColor Green
Write-Host "Function Name: $FunctionName" -ForegroundColor Cyan
