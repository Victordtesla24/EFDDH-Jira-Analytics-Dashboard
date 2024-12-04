#!/bin/bash

# Find all Python files and remove src. prefix from imports
find src -name "*.py" -type f -exec sed -i '' 's/from src\./from /g' {} +

# Add execute permissions
chmod +x fix_imports.sh
