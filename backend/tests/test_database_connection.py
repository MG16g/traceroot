from sqlalchemy import text
from sqlalchemy.orm import Session


def test_database_connection(db_session: Session) -> None:
    result = db_session.execute(text("SELECT 1"))

    assert result.scalar_one() == 1


def test_database_uses_isolated_postgresql(db_session: Session) -> None:
    result = db_session.execute(
        text("SELECT current_database(), current_user")
    )

    database_name, username = result.one()

    assert database_name == "traceroot_test_db"
    assert username == "traceroot_test_user"