import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db import get_db
from app.base import Base

# ── Test Database ──────────────────────────────────────────────────────────────
# We use a completely separate database for testing so we never touch real data.
# The URL format is: postgresql+driver://user:password@host:port/database_name
# Make sure farm_software_test exists in your postgres instance:
# docker exec -it farm_db psql -U farm -d farm_dev -c "CREATE DATABASE farm_software_test;"
TEST_DATABASE_URL = "postgresql+psycopg://farm:farm@localhost:5432/farm_software_test"

# Create a SQLAlchemy engine pointed at the test database
engine = create_engine(TEST_DATABASE_URL)

# sessionmaker builds a factory that creates database sessions on demand
TestingSession = sessionmaker(bind=engine)


# ── Fixtures ───────────────────────────────────────────────────────────────────
# Fixtures are reusable setup/teardown functions that pytest injects into tests.
# When a test function has a parameter that matches a fixture name, pytest
# automatically calls that fixture and passes the result in.
# Example: def test_something(client) <-- pytest sees "client" and runs the client fixture

@pytest.fixture(autouse=True)
def reset_db():
    # autouse=True means this fixture runs automatically before EVERY test,
    # even if the test doesn't explicitly ask for it.
    # This guarantees every test starts with a clean, empty database.
    Base.metadata.create_all(engine)    # Create all tables defined in our models
    yield                               # This is where the actual test runs
    Base.metadata.drop_all(engine)      # After the test, wipe everything clean


@pytest.fixture
def db():
    # This fixture provides a database session to tests that need direct DB access.
    # The try/finally ensures the session is always closed even if a test crashes.
    session = TestingSession()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db):
    # This fixture provides a TestClient - a fake HTTP client that talks to our
    # FastAPI app without needing a real running server.
    #
    # dependency_overrides replaces the real get_db (which connects to farm_dev)
    # with our test version (which connects to farm_software_test).
    # This is the key mechanism that makes tests use the test database.
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()    # Clean up the override after the test
