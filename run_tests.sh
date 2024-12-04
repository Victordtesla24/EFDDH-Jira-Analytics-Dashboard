#!/bin/bash

# Source common utilities
source "$(dirname "$0")/utils.sh" || {
    echo "Failed to source utils.sh"
    exit 1
}

# Function to run tests with specific markers
run_marked_tests() {
    local markers="$1"
    local description="$2"
    
    print_status "Running $description tests..."
    python -m pytest -v -m "$markers" \
        --cov=src \
        --cov-report=term-missing \
        --cov-report=html \
        src/tests/ui/dashboard/ || return 1
    print_status "✓ $description tests completed"
}

# Main function
main() {
    print_status "Starting test suite execution..."
    
    # Setup virtual environment if needed
    if [ ! -d "venv" ]; then
        print_status "Setting up virtual environment..."
        python -m venv venv
        source venv/bin/activate
        pip install -r requirements.txt
    else
        source venv/bin/activate
    fi
    
    # 1. Run high priority dashboard functionality tests
    run_marked_tests "priority_high and dashboard" "Dashboard Functionality" || {
        print_error "Dashboard functionality tests failed"
        exit 1
    }
    
    # 2. Run high priority metrics tests
    run_marked_tests "priority_high and metrics" "Metrics" || {
        print_error "Metrics tests failed"
        exit 1
    }
    
    # 3. Run high priority visualization tests
    run_marked_tests "priority_high and visuals" "Visualization" || {
        print_error "Visualization tests failed"
        exit 1
    }
    
    # 4. Run medium priority tests
    run_marked_tests "priority_medium" "Medium Priority" || {
        print_warning "Some medium priority tests failed"
    }
    
    # 5. Run low priority tests
    run_marked_tests "priority_low" "Low Priority" || {
        print_warning "Some low priority tests failed"
    }
    
    # Generate coverage report
    coverage report
    
    print_status "Test suite execution completed"
}

# Run main function
main
