import os
import toml
import importlib.util
import pytest

def test_streamlit_directory_structure():
    """Test required directory structure for Streamlit deployment."""
    required_dirs = [
        ".streamlit",
        "src/components",
        "src/pages",
        "src/utils",
        "src/data",
        "src/config",
        "src/tests",
        "logs",
    ]

    for dir_path in required_dirs:
        assert os.path.isdir(dir_path), f"Missing required directory: {dir_path}"

def test_required_files_exist():
    """Test existence of required files for Streamlit deployment."""
    required_files = [
        ".streamlit/config.toml",
        "src/streamlit_app.py",
        "requirements.txt",
        "README.md",
        "setup.py",
        "pytest.ini",
    ]

    for file_path in required_files:
        assert os.path.isfile(file_path), f"Missing required file: {file_path}"

def test_streamlit_config():
    """Test Streamlit configuration settings."""
    config_path = ".streamlit/config.toml"
    assert os.path.isfile(config_path), "Streamlit config.toml not found"

    config = toml.load(config_path)

    # Check server settings
    assert "server" in config, "Missing server configuration"
    server_config = config["server"]
    assert not server_config.get("enableCORS", True), "CORS should be disabled"

    # Check logger settings
    if "logger" in config:
        logger_config = config["logger"]
        assert logger_config.get("level", "") == "INFO", "Logger level should be INFO"

def test_requirements():
    """Test required Python packages."""
    with open("requirements.txt", "r") as f:
        requirements = f.read()

    required_packages = [
        "streamlit>=1.24.0",
        "pandas>=1.5.0",
        "plotly>=5.13.0",
        "pytest>=7.3.1",
        "pytest-cov>=4.1.0",
    ]

    for package in required_packages:
        assert package in requirements, f"Missing required package: {package}"

def test_main_app_structure():
    """Test main Streamlit app structure and entry points."""
    app_path = "src/streamlit_app.py"
    assert os.path.isfile(app_path), "Main Streamlit app not found"

    # Import the app module
    spec = importlib.util.spec_from_file_location("streamlit_app", app_path)
    app_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(app_module)

    # Check for required functions
    required_functions = ["initialize_app", "run_app"]

    for func in required_functions:
        assert hasattr(app_module, func), f"Missing required function: {func}"

def test_pages_structure():
    """Test pages directory structure and content."""
    pages_dir = "src/pages"
    assert os.path.isdir(pages_dir), "Pages directory not found"

    # Check for required pages
    required_pages = ["1_📊_Analytics.py", "2_👥_Capacity.py"]

    for page in required_pages:
        page_path = os.path.join(pages_dir, page)
        assert os.path.isfile(page_path), f"Missing required page: {page}"

def test_setup_py():
    """Test setup.py configuration."""
    with open("setup.py", "r") as f:
        setup_content = f.read()

    required_setup_fields = [
        "name",
        "version",
        "packages",
        "install_requires",
        "python_requires",
    ]

    for field in required_setup_fields:
        assert field in setup_content, f"Missing required setup.py field: {field}"

def test_readme_content():
    """Test README.md content."""
    with open("README.md", "r") as f:
        readme = f.read()

    required_sections = [
        "# JIRA Analytics Dashboard",
        "## Installation",
        "## Usage",
        "## Features",
        "## Development",
    ]

    for section in required_sections:
        assert section in readme, f"Missing required README section: {section}"

def test_gitignore():
    """Test .gitignore configuration."""
    assert os.path.isfile(".gitignore"), ".gitignore file not found"

    with open(".gitignore", "r") as f:
        gitignore = f.read()

    required_ignores = [
        "__pycache__",
        "*.pyc",
        "*.pyo",
        "*.pyd",
        ".Python",
        "env/",
        "venv/",
        ".env",
        ".venv",
        "*.log",
        ".coverage",
        "htmlcov/",
        ".pytest_cache/",
    ]

    for ignore in required_ignores:
        assert ignore in gitignore, f"Missing required .gitignore entry: {ignore}"

def test_logging_configuration():
    """Test logging configuration."""
    log_dir = "logs"
    assert os.path.isdir(log_dir), "Logs directory not found"

    # Check logging utility
    logging_util_path = "src/utils/logging_config.py"
    assert os.path.isfile(logging_util_path), "Logging configuration utility not found"

def test_deployment_scripts():
    """Test deployment scripts."""
    required_scripts = ["run.sh", "verify_and_fix.sh", "utils.sh"]

    for script in required_scripts:
        assert os.path.isfile(script), f"Missing required script: {script}"
        # Check if script is executable
        assert os.access(script, os.X_OK), f"Script not executable: {script}"
