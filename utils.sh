#!/bin/bash

# ANSI color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print status messages
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

# Function to print error messages
print_error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

# Function to print warning messages
print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Function to setup virtual environment
setup_venv() {
    if [ ! -d "venv" ]; then
        print_status "Creating virtual environment..."
        python -m venv venv || {
            print_error "Failed to create virtual environment"
            return 1
        }
    fi
    
    print_status "Activating virtual environment..."
    source venv/bin/activate || {
        print_error "Failed to activate virtual environment"
        return 1
    }
    
    print_status "Installing dependencies..."
    pip install -r requirements.txt || {
        print_error "Failed to install dependencies"
        return 1
    }
    
    return 0
}

# Function to check Python version
check_python_version() {
    local required_version="3.8.0"
    local current_version=$(python -c 'import sys; print(".".join(map(str, sys.version_info[:3])))')
    
    if ! command -v python >/dev/null 2>&1; then
        print_error "Python is not installed"
        return 1
    fi
    
    if ! python -c "import sys; exit(0 if sys.version_info >= tuple(map(int, '${required_version}'.split('.'))) else 1)"; then
        print_error "Python version must be >= ${required_version} (current: ${current_version})"
        return 1
    fi
    
    print_status "Python version check passed (${current_version})"
    return 0
}

# Function to check required commands
check_required_commands() {
    local commands=("python" "pip" "pytest" "black" "isort" "flake8" "mypy")
    local missing=0
    
    for cmd in "${commands[@]}"; do
        if ! command -v "$cmd" >/dev/null 2>&1; then
            print_error "Required command not found: $cmd"
            missing=1
        fi
    done
    
    return $missing
}

# Function to check directory structure
check_directory_structure() {
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
    
    local missing=0
    for dir in "${required_dirs[@]}"; do
        if [ ! -d "$dir" ]; then
            print_error "Missing required directory: $dir"
            missing=1
        fi
    done
    
    return $missing
}

# Function to create missing directories
create_missing_directories() {
    local dirs=(
        ".streamlit"
        "src/components"
        "src/pages"
        "src/utils"
        "src/data"
        "src/config"
        "src/tests"
        "logs"
    )
    
    for dir in "${dirs[@]}"; do
        if [ ! -d "$dir" ]; then
            print_status "Creating directory: $dir"
            mkdir -p "$dir"
        fi
    done
}

# Function to check file permissions
check_file_permissions() {
    local files=("run.sh" "run_tests.sh" "utils.sh" "verify_and_fix.sh")
    local missing=0
    
    for file in "${files[@]}"; do
        if [ -f "$file" ]; then
            if [ ! -x "$file" ]; then
                print_warning "File not executable: $file"
                chmod +x "$file" || {
                    print_error "Failed to make $file executable"
                    missing=1
                }
            fi
        else
            print_error "Missing script: $file"
            missing=1
        fi
    done
    
    return $missing
}

# Export functions
export -f print_status
export -f print_error
export -f print_warning
export -f setup_venv
export -f check_python_version
export -f check_required_commands
export -f check_directory_structure
export -f create_missing_directories
export -f check_file_permissions
