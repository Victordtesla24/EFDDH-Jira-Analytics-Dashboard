#!/bin/bash

# Source common utilities
source "$(dirname "$0")/utils.sh" || {
    echo "Failed to source utils.sh"
    exit 1
}

# Function to verify Python code formatting
verify_formatting() {
    print_status "Verifying code formatting..."
    
    # Run black check
    if ! black --check src/; then
        print_warning "Code formatting issues detected, fixing..."
        black src/ || {
            print_error "Failed to format code"
            return 1
        }
        print_status "✓ Code formatting fixed"
    else
        print_status "✓ Code formatting verified"
    fi
    
    # Run isort check
    if ! isort --check-only src/; then
        print_warning "Import sorting issues detected, fixing..."
        isort src/ || {
            print_error "Failed to sort imports"
            return 1
        }
        print_status "✓ Import sorting fixed"
    else
        print_status "✓ Import sorting verified"
    fi
    
    return 0
}

# Function to verify code quality
verify_code_quality() {
    print_status "Verifying code quality..."
    
    # Run flake8
    if ! flake8 src/; then
        print_warning "Code style issues detected"
        return 1
    fi
    print_status "✓ Code style verified"
    
    # Run mypy
    if ! mypy src/; then
        print_warning "Type checking issues detected"
        return 1
    fi
    print_status "✓ Type checking verified"
    
    return 0
}

# Function to verify tests
verify_tests() {
    print_status "Running test suite..."
    
    # Run tests with coverage
    if ! ./run_tests.sh; then
        print_error "Tests failed"
        return 1
    fi
    print_status "✓ All tests passed"
    
    return 0
}

# Function to verify dependencies
verify_dependencies() {
    print_status "Verifying dependencies..."
    
    # Check requirements.txt
    if [ ! -f "requirements.txt" ]; then
        print_error "requirements.txt not found"
        return 1
    fi
    
    # Verify all dependencies are installed
    if ! pip install -r requirements.txt; then
        print_error "Failed to install dependencies"
        return 1
    fi
    print_status "✓ Dependencies verified"
    
    return 0
}

# Function to verify Streamlit configuration
verify_streamlit_config() {
    print_status "Verifying Streamlit configuration..."
    
    local config_file=".streamlit/config.toml"
    if [ ! -f "$config_file" ]; then
        print_error "Streamlit config not found"
        return 1
    fi
    
    # Check required settings
    local required_settings=(
        "enableCORS = false"
        "runOnSave = true"
        "level = \"INFO\""
    )
    
    local missing=0
    for setting in "${required_settings[@]}"; do
        if ! grep -q "$setting" "$config_file"; then
            print_error "Missing setting in config.toml: $setting"
            missing=1
        fi
    done
    
    if [ $missing -eq 1 ]; then
        return 1
    fi
    
    print_status "✓ Streamlit configuration verified"
    return 0
}

# Function to verify documentation
verify_documentation() {
    print_status "Verifying documentation..."
    
    # Check README.md
    if [ ! -f "README.md" ]; then
        print_error "README.md not found"
        return 1
    fi
    
    # Run markdownlint if available
    if command -v markdownlint >/dev/null 2>&1; then
        if ! markdownlint README.md; then
            print_warning "Markdown linting issues detected"
            return 1
        fi
    else
        print_warning "markdownlint not installed, skipping markdown verification"
    fi
    
    print_status "✓ Documentation verified"
    return 0
}

# Function to verify Streamlit deployment requirements
verify_streamlit_deployment() {
    print_status "Verifying Streamlit deployment requirements..."
    
    # Check .streamlit directory
    if [ ! -d ".streamlit" ]; then
        print_warning "Creating .streamlit directory..."
        mkdir .streamlit
    fi
    
    # Check config.toml
    if [ ! -f ".streamlit/config.toml" ]; then
        print_error ".streamlit/config.toml is missing"
        return 1
    fi
    
    # Check sample data
    if [ ! -f "data/sample.csv" ]; then
        print_error "data/sample.csv is missing"
        return 1
    fi
    
    # Verify secrets handling
    if ! grep -q "st.secrets" src/config/settings.py; then
        print_warning "Secrets handling not implemented in settings.py"
        return 1
    fi
    
    print_status "✓ Streamlit deployment requirements verified"
    return 0
}

# Main function
main() {
    print_status "Starting deployment verification..."
    
    # Create required directories
    create_missing_directories
    
    # Make scripts executable
    chmod +x run.sh run_tests.sh utils.sh verify_and_fix.sh
    
    # Verify Python version
    check_python_version || exit 1
    
    # Setup virtual environment
    setup_venv || exit 1
    
    # Run all verifications
    local verification_failed=false
    
    verify_formatting || verification_failed=true
    verify_code_quality || verification_failed=true
    verify_tests || verification_failed=true
    verify_dependencies || verification_failed=true
    verify_streamlit_config || verification_failed=true
    verify_documentation || verification_failed=true
    verify_streamlit_deployment || verification_failed=true
    
    if [ "$verification_failed" = true ]; then
        print_error "Some verifications failed"
        exit 1
    fi
    
    print_status "✓ All verifications passed"
    print_status "Ready for deployment!"
}

# Run main function
main
