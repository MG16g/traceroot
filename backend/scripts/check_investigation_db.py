from sqlalchemy import text

from app.core.database import engine


def main():
    query = text(
        """
        SELECT
            id,
            incident_id,
            status,
            iteration,
            current_step,
            created_at
        FROM investigations
        WHERE incident_id = :incident_id
        ORDER BY created_at DESC
        """
    )

    with engine.connect() as connection:
        rows = connection.execute(
            query,
            {
                "incident_id": "INC-001",
            },
        ).fetchall()

    print("\n===================================")
    print("TraceRoot Investigation DB Check")
    print("===================================\n")

    if not rows:
        print("No persisted investigation found for INC-001.")
        return

    print(f"Found {len(rows)} investigation(s):\n")

    for row in rows:
        print(f"ID:           {row.id}")
        print(f"Incident ID:  {row.incident_id}")
        print(f"Status:       {row.status}")
        print(f"Iterations:   {row.iteration}")
        print(f"Current Step: {row.current_step}")
        print(f"Created At:   {row.created_at}")
        print("-----------------------------------")


if __name__ == "__main__":
    main()