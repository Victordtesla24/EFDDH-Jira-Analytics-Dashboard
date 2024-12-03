#!/bin/bash

# Source common utilities
# shellcheck source=utils.sh
source "$(dirname "$0")/utils.sh" || {
    echo "Failed to source utils.sh"
    exit 1
}

# Function to check git status
check_git_status() {
    if ! git rev-parse --is-inside-work-tree > /dev/null 2>&1; then
        print_error "Not a git repository"
        return 1
    fi
    
    if [ -n "$(git status --porcelain)" ]; then
        return 0
    else
        print_warning "No changes to commit"
        return 1
    fi
}

# Function to commit and push changes
commit_changes() {
    local message="$1"
    if check_git_status; then
        print_status "Committing changes..."
        git add . || {
            print_error "Failed to stage changes"
            return 1
        }
        git commit -m "$message" || {
            print_error "Failed to commit changes"
            return 1
        }
        if git remote get-url origin &>/dev/null; then
            git push origin "$(git rev-parse --abbrev-ref HEAD)" || {
                print_error "Failed to push changes"
                return 1
            }
            print_status "Changes pushed to repository"
        else
            print_warning "No remote repository configured, skipping push"
        fi
    fi
    return 0
}

# Function to verify Streamlit directory structure
verify_directory_structure() {
    print_status "Verifying directory structure..."
    
    local required_dirs=(
        ".streamlit"
        "src/components"
        "src/pages"
        "src/utils"
        "src/data"
        "src/config"
        "src/tests"
        "logs"
    )

    local required_files=(
        ".streamlit/config.toml"
        "src/streamlit_app.py"
        "requirements.txt"
        "README.md"
        "setup.py"
        "pytest.ini"
    )

    local missing=0
    for dir in "${required_dirs[@]}"; do
        if [ ! -d "$dir" ]; then
            print_error "Missing directory: $dir"
            missing=1
        else
            print_status "✓ Directory verified: $dir"
        fi
    done

    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            print_error "Missing file: $file"
            missing=1
        else
            print_status "✓ File verified: $file"
        fi
    done

    return $missing
}

# Function to verify Streamlit configuration
verify_streamlit_config() {
    print_status "Verifying Streamlit configuration..."
    
    local config_file=".streamlit/config.toml"
    if [ ! -f "$config_file" ]; then
        print_error "config.toml not found"
        return 1
    fi

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
        else
            print_status "✓ Config setting verified: $setting"
        fi
    done

    return $missing
}

# Function to verify Python dependencies
verify_dependencies() {
    print_status "Verifying Python dependencies..."
    
    local required_packages=(
        "streamlit>=1.24.0"
        "pandas>=1.5.0"
        "plotly>=5.13.0"
        "pytest>=7.3.1"
        "pytest-cov>=4.1.0"
        "black>=23.3.0"
        "flake8>=6.0.0"
        "mypy>=1.3.0"
        "isort>=5.12.0"
    )

    local missing=0
    for package in "${required_packages[@]}"; do
        if ! grep -q "$package" requirements.txt; then
            print_error "Missing package in requirements.txt: $package"
            missing=1
        else
            print_status "✓ Package verified: $package"
        fi
    done

    return $missing
}

# Function to run tests and check coverage
run_tests() {
    print_status "Running tests and checking coverage..."
    
    # Run pytest with coverage
    if ! pytest --cov=src --cov-report=term-missing --cov-report=html; then
        print_error "Tests failed!"
        return 1
    fi
    print_status "✓ All tests passed successfully"

    # Check coverage threshold
    local coverage_result
    coverage_result=$(coverage report | tail -n 1 | awk '{print $4}' | sed 's/%//')
    if [ "${coverage_result%.*}" -lt 80 ]; then
        print_warning "Code coverage is below 80%: $coverage_result%"
        return 1
    fi
    print_status "✓ Code coverage is satisfactory: $coverage_result%"

    return 0
}

# Function to verify code quality
verify_code_quality() {
    print_status "Verifying code quality..."
    local failed=0
    
    # Run black
    print_status "Running black formatter..."
    if ! black --check src/; then
        print_error "Code formatting issues detected"
        failed=1
    else
        print_status "✓ Code formatting verified"
    fi

    # Run isort
    print_status "Running isort..."
    if ! isort --check-only src/; then
        print_error "Import sorting issues detected"
        failed=1
    else
        print_status "✓ Import sorting verified"
    fi

    # Run flake8
    print_status "Running flake8..."
    if ! flake8 src/; then
        print_error "Code style issues detected"
        failed=1
    else
        print_status "✓ Code style verified"
    fi

    # Run mypy
    print_status "Running type checker..."
    if ! mypy src/; then
        print_error "Type checking issues detected"
        failed=1
    else
        print_status "✓ Type checking verified"
    fi

    return $failed
}

# Function to fix issues using verify_and_fix.sh
fix_issues() {
    print_status "Attempting to fix issues..."
    
    if [ -f "verify_and_fix.sh" ]; then
        if ! bash verify_and_fix.sh; then
            print_error "Failed to fix issues"
            return 1
        fi
        print_status "✓ Issues fixed successfully"
        return 0
    else
        print_error "verify_and_fix.sh not found"
        return 1
    fi
}

# Function to run the Streamlit app
run_app() {
    print_status "Starting Streamlit app..."
    if ! command -v streamlit &>/dev/null; then
        print_error "Streamlit not found. Please install dependencies first."
        return 1
    fi
    streamlit run src/streamlit_app.py
}

# Main function
main() {
    print_status "Starting deployment verification process..."

    # Setup virtual environment
    setup_venv || {
        print_error "Failed to setup virtual environment"
        exit 1
    }

    # Run all verifications
    local verification_failed=false

    verify_directory_structure || verification_failed=true
    verify_streamlit_config || verification_failed=true
    verify_dependencies || verification_failed=true
    verify_code_quality || verification_failed=true
    run_tests || verification_failed=true

    # Attempt to fix issues if any verification failed
    if [ "$verification_failed" = true ]; then
        print_warning "Some verifications failed, attempting to fix..."
        if fix_issues; then
            # Commit changes if fixes were applied
            commit_changes "Fix: Applied automated fixes from verification process"
        else
            print_error "Failed to fix all issues"
            exit 1
        fi
    fi

    # Final verification after fixes
    if verify_directory_structure && \
       verify_streamlit_config && \
       verify_dependencies && \
       verify_code_quality && \
       run_tests; then
        print_status "✓ All verifications passed!"
        commit_changes "Update: Successful deployment verification"
        print_status "Starting the app..."
        run_app
    else
        print_error "Verification failed after fixes. Please check the errors above."
        exit 1
    fi
}

# Parse command line arguments
while getopts ":hs" opt; do
    case ${opt} in
        h )
            echo "Usage: $0 [-h] [-s]"
            echo "  -h  Display this help message"
            echo "  -s  Skip git operations"
            exit 0
            ;;
        s )
            SKIP_GIT=true
            ;;
        \? )
            print_error "Invalid option: -$OPTARG" 1>&2
            exit 1
            ;;
    esac
done

# Run main function
main
