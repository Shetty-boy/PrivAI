"""
Pytest configuration and shared fixtures.
Sets up the database with an in-memory SQLite for tests.
"""
import sys
import os
import pytest

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Use a test database to avoid polluting real data
os.environ.setdefault("PAI_TEST_MODE", "1")


@pytest.fixture(scope="session", autouse=True)
def initialize_test_db():
    """Initialize the database once per test session."""
    from app.storage.database import init_db
    init_db()
    yield
