from storage.database import Base, engine
from storage.models import Filing


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully.")


if __name__ == "__main__":
    init_db()