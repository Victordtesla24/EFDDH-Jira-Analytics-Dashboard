#!/bin/bash

# Define color codes for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Function to print status messages with timestamps
print_status() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')] [STATUS] ${GREEN}$1${NC}"
}

# Function to print error messages with timestamps
print_error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] [ERROR] $1${NC}"
}

# Function to print warning messages with timestamps
print_warning() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] [WARNING] $1${NC}"
}

# Function to setup virtual environment
setup_venv() {
    if [ ! -d ".venv" ]; then
        print_status "Creating virtual environment..."
        python3 -m venv .venv || {
            print_error "Failed to create virtual environment"
            return 1
        }
        source .venv/bin/activate || return 1
        pip install -r requirements.txt || {
            print_error "Failed to install dependencies"
            return 1
        }
        print_status "✓ Virtual environment created and dependencies installed"
    else
        source .venv/bin/activate || return 1
        print_status "✓ Using existing virtual environment"
    fi
    return 0
}

# Function to cleanup on exit
cleanup() {
    if [ -n "$VIRTUAL_ENV" ]; then
        deactivate 2>/dev/null
    fi
    print_status "Cleanup completed"
}

# Set cleanup trap
trap cleanup EXIT INT TERM
