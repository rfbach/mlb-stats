#!/usr/bin/env python3
"""Build Lambda deployment package with dependencies."""
import os
import shutil
import subprocess
import zipfile
from pathlib import Path

# Paths
TERRAFORM_DIR = Path(__file__).parent
PROJECT_ROOT = TERRAFORM_DIR.parent
BUILD_DIR = TERRAFORM_DIR / ".terraform" / "lambda_build"
LAMBDA_ZIP = TERRAFORM_DIR / ".terraform" / "lambda_function.zip"
REQUIREMENTS_FILE = PROJECT_ROOT / "requirements.txt"

# Create build directory
BUILD_DIR.mkdir(parents=True, exist_ok=True)

# Clean previous build
if BUILD_DIR.exists():
    shutil.rmtree(BUILD_DIR)
BUILD_DIR.mkdir(parents=True, exist_ok=True)

# Install dependencies
print("Installing dependencies...")
subprocess.run(
    ["pip", "install", "-r", str(REQUIREMENTS_FILE), "-t", str(BUILD_DIR)],
    check=True
)

# Copy source code to src/ subdirectory
print("Copying source code...")
src_dir = PROJECT_ROOT / "src"
dest_src_dir = BUILD_DIR / "src"
dest_src_dir.mkdir(exist_ok=True)

for item in src_dir.iterdir():
    if item.name.startswith("__pycache__"):
        continue
    if item.is_file() and item.suffix == ".py":
        shutil.copy(item, dest_src_dir / item.name)
    elif item.is_dir():
        dest = dest_src_dir / item.name
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(item, dest)

# Create zip file
print(f"Creating deployment package: {LAMBDA_ZIP}")
if LAMBDA_ZIP.exists():
    LAMBDA_ZIP.unlink()

with zipfile.ZipFile(LAMBDA_ZIP, "w", zipfile.ZIP_DEFLATED) as zf:
    for root, dirs, files in os.walk(BUILD_DIR):
        # Skip __pycache__ directories
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        
        for file in files:
            if not file.endswith(".pyc"):
                file_path = Path(root) / file
                arcname = file_path.relative_to(BUILD_DIR)
                zf.write(file_path, arcname)

print(f"Lambda package created: {LAMBDA_ZIP}")
