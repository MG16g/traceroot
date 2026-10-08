import pytest

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from tests.db_safety import validate_test_database_url


@pytest.fixture(scope="session")
def test_engine():
    """
    Dedicated PostgreSQL engine for integration tests.

    Never use the development database engine here.
    """
    url = validate_test_database_url()

    engine = create_engine(
        url,
        pool_pre_ping=True,
    )

    try:
        with engine.connect() as connection:
            result = connection.execute(
                text("""
                    SELECT
                        current_database(),
                        current_user
                """)
            ).one()

            database_name, username = result

            if database_name != "traceroot_test_db":
                raise RuntimeError(
                    "Unsafe database connection: "
                    f"{database_name}"
                )

            if username != "traceroot_test_user":
                raise RuntimeError(
                    "Unexpected PostgreSQL test user: "
                    f"{username}"
                )

        yield engine

    finally:
        engine.dispose()


@pytest.fixture
def db_session(test_engine):
    """
    Isolated database session.

    All database changes are rolled back after the test,
    even if application code calls session.commit().
    """
    with test_engine.connect() as connection:
        transaction = connection.begin()

        session = Session(
            bind=connection,
            join_transaction_mode="create_savepoint",
            expire_on_commit=False,
        )

        try:
            yield session
        finally:
            session.close()
            transaction.rollback()