#!/bin/bash

# Source common utilities
source "$(dirname "$0")/utils.sh" || {
    echo "Failed to source utils.sh"
    exit 1
}

# Function to fix code formatting
fix_formatting() {
    print_status "Fixing code formatting..."
    black src/ || return 1
    print_status "✓ Code formatting fixed"
}

# Function to fix import sorting
fix_imports() {
    print_status "Fixing import sorting..."
    isort src/ || return 1
    print_status "✓ Import sorting fixed"
}

# Function to fix line length issues
fix_line_length() {
    print_status "Fixing line length issues..."
    find src -type f -name "*.py" -exec bash -c '
        for file do
            awk -v len=79 "
                length > len {
                    # Split long strings into multiple lines
                    if (\$0 ~ /\".*\"/ || \$0 ~ /'\''.*'\''/) {
                        gsub(/\".*\"/, \"\\\\n&\", \$0)
                        gsub(/'\''.*'\''/, \"\\\\n&\", \$0)
                    }
                    # Add line continuation for other long lines
                    else {
                        sub(/.{79}/, \"&\\\\n\", \$0)
                    }
                }
                {print}
            " \$file > \$file.tmp && mv \$file.tmp \$file
        done
    ' bash {} +
    print_status "✓ Line length issues fixed"
}

# Function to fix unused imports
fix_unused_imports() {
    print_status "Fixing unused imports..."
    autoflake --in-place --remove-all-unused-imports --recursive src/ || return 1
    print_status "✓ Unused imports fixed"
}

# Function to fix whitespace issues
fix_whitespace() {
    print_status "Fixing whitespace issues..."
    find src -type f -name "*.py" -exec sed -i '' -e 's/[ \t]*$//' {} +
    print_status "✓ Whitespace issues fixed"
}

# Function to fix variable naming issues
fix_variable_names() {
    print_status "Fixing variable naming issues..."
    find src -type f -name "*.py" -exec bash -c '
        for file do
            # Replace unused variables with _
            sed -i "" "s/\([a-zA-Z_][a-zA-Z0-9_]*\).*F841.*local variable.*never used/_ = &/" \$file
        done
    ' bash {} +
    print_status "✓ Variable naming issues fixed"
}

# Main function
main() {
    print_status "Starting code quality fixes..."
    
    # Fix formatting issues
    fix_formatting || {
        print_error "Failed to fix formatting"
        exit 1
    }
    
    # Fix import sorting
    fix_imports || {
        print_error "Failed to fix imports"
        exit 1
    }
    
    # Fix line length issues
    fix_line_length || {
        print_error "Failed to fix line length issues"
        exit 1
    }
    
    # Fix unused imports
    fix_unused_imports || {
        print_error "Failed to fix unused imports"
        exit 1
    }
    
    # Fix whitespace issues
    fix_whitespace || {
        print_error "Failed to fix whitespace issues"
        exit 1
    }
    
    # Fix variable naming issues
    fix_variable_names || {
        print_error "Failed to fix variable naming issues"
        exit 1
    }
    
    print_status "✓ All code quality fixes completed"
    
    # Run flake8 to verify fixes
    if flake8 src/; then
        print_status "✓ Code quality verification passed"
    else
        print_warning "Some code quality issues remain"
        return 1
    fi
}

# Run main function
main
