import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def pytest_configure(config):
    """Configure pytest settings"""
    config.addinivalue_line(
        'markers',
        'selenium: mark test as requiring selenium'
    )
    
    # Set debug config via inicfg
    config._inicache['selenium_exclude_debug'] = ['screenshots']
    config._inicache['selenium_capture_debug'] = 'false'
    config._inicache['dash_port'] = '8050'
    config._inicache['dash_host'] = 'localhost'

@pytest.fixture(scope="session")
def selenium_config():
    """Selenium configuration with proper debug settings"""
    return {
        'exclude_debug': ['screenshots'],
        'base_url': 'http://localhost:8050',
        'capabilities': {
            'browserName': 'chrome',
            'goog:chromeOptions': {
                'args': ['--headless', '--no-sandbox', '--disable-gpu']
            }
        }
    }

@pytest.fixture
def chrome_options():
    """Chrome options for testing"""
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-dev-shm-usage')
    return options

@pytest.fixture
def selenium(chrome_options):
    """Set up the Selenium WebDriver with Chrome options"""
    driver = webdriver.Chrome(options=chrome_options)
    yield driver
    driver.quit()

@pytest.fixture
def dash_thread_server():
    """Fixture to handle Dash server in a separate thread"""
    import threading
    import time
    from werkzeug.serving import make_server

    def run_server(app, port):
        server = make_server('localhost', port, app)
        thread = threading.Thread(target=server.serve_forever)
        thread.setDaemon(True)
        thread.start()
        time.sleep(1)  # Give the server time to start

    return run_server

@pytest.fixture(autouse=True)
def cleanup_test_env():
    """Setup and teardown for each test"""
    # Pre-test setup
    yield
    # Post-test cleanup
    from pathlib import Path
    import shutil
    
    # Clean up any temporary files
    test_files = ['test_data.csv', '.pytest_cache']
    for file in test_files:
        path = Path(file)
        if path.is_file():
            path.unlink()
        elif path.is_dir():
            shutil.rmtree(path)

@pytest.fixture(scope="session", autouse=True)
def configure_html_report_env(request):
    """Configure the HTML report environment"""
    request.config._metadata.update({
        'Project': 'Jira Dashboard',
        'Platform': 'Local Testing'
    })

    yield

    # Clear any test artifacts
    from pathlib import Path
    import shutil
    
    for path in ['.pytest_cache', '__pycache__', 'test_data.csv']:
        try:
            p = Path(path)
            if p.is_file():
                p.unlink()
            elif p.is_dir():
                shutil.rmtree(p)
        except Exception as e:
            print(f"Failed to clean {path}: {e}")