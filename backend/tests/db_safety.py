from pathlib import Path

from dotenv import dotenv_values
from sqlalchemy.engine import make_url

from app.core.config import settings


BACKEND_DIR = Path(__file__).resolve().parents[1]


def validate_test_database_url() -> str:
    """Validate the dedicated PostgreSQL test configuration."""

    config = dotenv_values(BACKEND_DIR / ".env.test")
    test_url_value = config.get("TEST_DATABASE_URL")

    if not test_url_value:
        raise RuntimeError(
            "TEST_DATABASE_URL is missing from backend/.env.test"
        )

    test_url = make_url(test_url_value)
    development_url = make_url(settings.database_url)

    if test_url.drivername != "postgresql+psycopg":
        raise RuntimeError(
            "Test database must use postgresql+psycopg."
        )

    if test_url.database != "traceroot_test_db":
        raise RuntimeError(
            "Unexpected test database name."
        )

    if test_url.username != "traceroot_test_user":
        raise RuntimeError(
            "Unexpected test database username."
        )

    def identity(url):
        return (
            url.get_backend_name(),
            url.host,
            url.port or 5432,
            url.database,
        )

    if identity(test_url) == identity(development_url):
        raise RuntimeError(
            "Test database cannot be the development database."
        )

    if development_url.database == test_url.database:
        raise RuntimeError(
            "Development and test database names must differ."
        )

    return test_url_value