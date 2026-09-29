from sqlalchemy import text

from storage.database import engine


def test_connection() -> None:
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        print(f"Database connection successful: {result.scalar()}")


if __name__ == "__main__":
    test_connection()