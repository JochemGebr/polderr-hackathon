import os
from pathlib import Path

from dotenv import load_dotenv
from sqlmodel import Session, SQLModel, create_engine

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./dev.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})


def create_tables() -> bool:
    """Create DB tables.

    Returns True when a new SQLite DB file was created by this call (i.e. the
    file did not exist before). Returns False otherwise.
    """
    created_new = False

    existed = None
    try:
        # detect sqlite file path if present
        if engine.url.get_backend_name() == "sqlite":
            db_path = engine.url.database
            if db_path and db_path != ":memory":
                base = Path(__file__).resolve().parents[1]
                full = Path(db_path)
                if not full.is_absolute():
                    full = (base / db_path).resolve()
                existed = full.exists()
    except Exception:
        existed = None

    SQLModel.metadata.create_all(engine)

    if engine.url.get_backend_name() == "sqlite" and existed is False:
        created_new = True

    return created_new


def get_session():
    with Session(engine) as session:
        yield session
