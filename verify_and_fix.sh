#!/bin/bash

# Source common utilities
# shellcheck source=utils.sh
source "$(dirname "$0")/utils.sh" || {
    echo "Failed to source utils.sh"
    exit 1
}

# Function to create/update Streamlit config
update_streamlit_config() {
    print_status "Updating Streamlit configuration..."
    mkdir -p .streamlit || return 1
    cat > .streamlit/config.toml << 'EOF' || return 1
[server]
enableCORS = false
runOnSave = true

[theme]
primaryColor = "#FF4B4B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"

[logger]
level = "INFO"

[client]
toolbarMode = "auto"
showErrorDetails = true

[runner]
fastReruns = true
EOF
    print_status "✓ Streamlit config updated"
    return 0
}

# Function to create/update conftest.py
update_conftest() {
    print_status "Updating test configuration..."
    mkdir -p src/tests || return 1
    cat > src/tests/conftest.py << 'EOF' || return 1
import pandas as pd
import pytest
from unittest.mock import MagicMock

@pytest.fixture
def test_data():
    """Create sample data for testing."""
    return pd.DataFrame({
        "Issue Type": ["Story", "Task", "Bug"],
        "Priority": ["High", "Low", "Medium"],
        "Status": ["Done", "Done", "In Progress"],
        "Story Points": [3, 8, 5],
        "Created": ["2024-01-02", "2024-01-03", "2024-01-04"],
        "Epic Link": ["EPIC-2", "EPIC-1", "EPIC-3"],
        "Epic Name": ["Epic 2", "Epic 1", "Epic 3"]
    })

@pytest.fixture
def test_data_path(tmp_path):
    """Create a temporary test data file."""
    data_file = tmp_path / "test_data.csv"
    test_data = pd.DataFrame({
        "Issue Type": ["Story", "Task", "Bug"],
        "Priority": ["High", "Medium", "Low"],
        "Status": ["Done", "In Progress", "To Do"]
    })
    test_data.to_csv(data_file, index=False)
    return data_file

@pytest.fixture
def mock_streamlit():
    """Mock Streamlit components."""
    mock = MagicMock()
    mock.title = MagicMock()
    mock.header = MagicMock()
    mock.plotly_chart = MagicMock()
    mock.metric = MagicMock()
    mock.error = MagicMock()
    mock.warning = MagicMock()
    mock.success = MagicMock()
    mock.info = MagicMock()
    mock.dataframe = MagicMock()
    mock.columns = MagicMock(return_value=[MagicMock(), MagicMock(), MagicMock()])
    return mock
EOF
    print_status "✓ Test configuration updated"
    return 0
}

# Function to update pytest configuration
update_pytest_config() {
    print_status "Updating pytest configuration..."
    cat > pytest.ini << 'EOF' || return 1
[pytest]
testpaths = src/tests
python_files = test_*.py
python_functions = test_*
addopts = --cov=src --cov-report=html --cov-report=term-missing --cov-fail-under=80
markers =
    integration: marks tests as integration tests
    unit: marks tests as unit tests
    slow: marks tests as slow running
EOF
    print_status "✓ Pytest configuration updated"
    return 0
}

# Function to create/update logging configuration
update_logging_config() {
    print_status "Updating logging configuration..."
    mkdir -p src/utils || return 1
    cat > src/utils/logging_config.py << 'EOF' || return 1
import logging
import os
from datetime import datetime

def setup_logging():
    """Configure logging for the application."""
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"app_{timestamp}.log")

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

    # Set specific log levels for different modules
    logging.getLogger("streamlit").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("matplotlib").setLevel(logging.WARNING)

    return logging.getLogger(__name__)
EOF
    print_status "✓ Logging configuration updated"
    return 0
}

# Function to fix common code issues
fix_code_issues() {
    print_status "Fixing code issues..."

    # Run black formatter
    if command -v black >/dev/null 2>&1; then
        print_status "Running black formatter..."
        black src/ || return 1
        print_status "✓ Code formatting completed"
    else
        print_warning "black not installed, skipping formatting"
    fi

    # Run isort
    if command -v isort >/dev/null 2>&1; then
        print_status "Running isort..."
        isort src/ || return 1
        print_status "✓ Import sorting completed"
    else
        print_warning "isort not installed, skipping import sorting"
    fi

    # Create required directories if missing
    local dirs=(
        "src/components"
        "src/pages"
        "src/utils"
        "src/data"
        "src/config"
        "src/tests/components"
        "src/tests/data"
        "src/tests/integration"
        "src/tests/pages"
        "src/tests/utils"
        "logs"
    )

    for dir in "${dirs[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir" || return 1
            touch "$dir/__init__.py" || return 1
            print_status "✓ Created directory and __init__.py: $dir"
        fi
    done
    return 0
}

# Function to update requirements
update_requirements() {
    print_status "Updating requirements.txt..."
    cat > requirements.txt << 'EOF' || return 1
streamlit>=1.24.0
pandas>=1.5.0
plotly>=5.13.0
pytest>=7.3.1
pytest-cov>=4.1.0
pytest-mock>=3.10.0
black>=23.3.0
flake8>=6.0.0
mypy>=1.3.0
isort>=5.12.0
python-dotenv>=1.0.0
requests>=2.31.0
EOF
    print_status "✓ Requirements updated"
    return 0
}

# Main function
main() {
    print_status "Starting verification and fix process..."

    # Setup virtual environment
    setup_venv || {
        print_error "Failed to setup virtual environment"
        exit 1
    }

    # Update all configurations
    update_streamlit_config || exit 1
    update_conftest || exit 1
    update_pytest_config || exit 1
    update_logging_config || exit 1
    update_requirements || exit 1

    # Fix code issues
    fix_code_issues || {
        print_error "Failed to fix code issues"
        exit 1
    }

    print_status "✓ All fixes completed successfully"
}

# Parse command line arguments
while getopts ":h" opt; do
    case ${opt} in
        h )
            echo "Usage: $0 [-h]"
            echo "  -h  Display this help message"
            exit 0
            ;;
        \? )
            print_error "Invalid option: -$OPTARG" 1>&2
            exit 1
            ;;
    esac
done

# Run main function
main
