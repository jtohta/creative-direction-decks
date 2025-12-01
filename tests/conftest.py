"""
Pytest configuration and shared fixtures for test isolation.

Per constitution requirements:
- Tests must be isolated (own data, no shared state)
- Tests must support parallel execution
- Tests must clean up resources after completion
"""

import pytest
import tempfile
import shutil
from pathlib import Path


@pytest.fixture
def temp_dir():
    """
    Provide isolated temporary directory for each test.
    
    Automatically cleaned up after test completion.
    Supports parallel test execution.
    """
    temp_path = tempfile.mkdtemp()
    yield Path(temp_path)
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def sample_image_data():
    """
    Provide real JPEG image data for testing file uploads.
    
    Returns binary data from actual test image file.
    Uses real JPEG file (tests/fixtures/test_image.jpg) instead of mocks.
    """
    test_image_path = Path(__file__).parent / "fixtures" / "test_image.jpg"
    with open(test_image_path, "rb") as f:
        return f.read()


@pytest.fixture
def sample_image_file():
    """
    Provide path to real test image file.
    
    Returns Path object to test_image.jpg for file-based tests.
    """
    return Path(__file__).parent / "fixtures" / "test_image.jpg"


@pytest.fixture
def mock_session_state():
    """
    Provide simple dict for Streamlit session state in tests.
    
    Note: Not a "mock" per se - just a dict that behaves like st.session_state.
    For unit/integration tests, a dict is sufficient since we're not testing
    Streamlit's internal session management.
    """
    return {}


@pytest.fixture(scope="function")
def isolated_session_id():
    """
    Generate unique session ID for each test to prevent collision.
    
    Uses UUID4 for uniqueness in parallel execution.
    """
    import uuid
    return str(uuid.uuid4())


# VCR (HTTP Recording) Configuration
@pytest.fixture(scope="module")
def vcr_config():
    """
    Configuration for pytest-vcr HTTP recording.
    
    Filters sensitive headers from recordings.
    Records on first run, replays on subsequent runs.
    """
    return {
        "filter_headers": [
            "authorization",
            "x-amz-date",
            "x-amz-content-sha256",
            "x-amz-security-token",
        ],
        "record_mode": "once",  # Record on first run, replay thereafter
        "match_on": ["method", "scheme", "host", "port", "path", "query"],
    }


# Pytest configuration
def pytest_configure(config):
    """
    Configure pytest with custom markers.
    """
    config.addinivalue_line(
        "markers", "vcr: mark test to use VCR for HTTP recording"
    )
    config.addinivalue_line(
        "markers", "e2e: mark test as end-to-end (requires browser)"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "unit: mark test as unit test (pure functions only)"
    )

