#!/bin/bash

# Source common utilities
source "$(dirname "$0")/utils.sh" || {
    echo "Failed to source utils.sh"
    exit 1
}

# Function to fix streamlit imports
fix_streamlit_imports() {
    print_status "Fixing streamlit imports..."
    find src -type f -name "*.py" -exec sed -i '' '
        s/^import streamlit as s$/import streamlit as st/g
        s/^from streamlit import /import streamlit as st\n&/g
        s/\<s\./st./g
    ' {} +
}

# Function to fix pytest imports
fix_pytest_imports() {
    print_status "Fixing pytest imports..."
    find src/tests -type f -name "test_*.py" -exec sed -i '' '
        /^import pytest$/!i\
import pytest
        s/@pytest\.mark/@pytest.mark/g
        s/@pytest\.fixture/@pytest.fixture/g
    ' {} +
}

# Function to fix typing imports
fix_typing_imports() {
    print_status "Fixing typing imports..."
    find src -type f -name "*.py" -exec sed -i '' '
        /^from typing import/!i\
from typing import Dict, List, Optional, Union, Any
    ' {} +
}

# Function to fix unused imports
fix_unused_imports() {
    print_status "Fixing unused imports..."
    find src -type f -name "*.py" -exec sed -i '' '
        /^from.*import.*as.*$/d
        /^import.*as.*$/d
        /^from.*import.*$/!s/^import /from /
    ' {} +
}

# Function to fix line lengths
fix_line_lengths() {
    print_status "Fixing line lengths..."
    find src -type f -name "*.py" -exec sed -i '' '
        s/.\{79\}/&\\\n    /g
    ' {} +
}

# Main function
main() {
    print_status "Starting import fixes..."
    
    fix_streamlit_imports
    fix_pytest_imports
    fix_typing_imports
    fix_unused_imports
    fix_line_lengths
    
    print_status "✓ Import fixes completed"
}

# Run main function
main
