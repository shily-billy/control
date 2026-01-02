# app/database/session.py
"""
مدیریت اتصال به دیتابیس
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from pathlib import Path
import os

# مسیر پوشه data
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

# مسیر فایل database
DATABASE_PATH = DATA_DIR / "control.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# ساخت Engine
engine = create_engine(
    DATABASE_URL,
    echo=False,  # True برای دیدن SQL queries
    connect_args={"check_same_thread": False}  # برای SQLite
)

# ساخت SessionLocal
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def init_db():
    """
    ساخت تمام جداول در دیتابیس
    """
    from app.database.models import Base
    Base.metadata.create_all(bind=engine)


@contextmanager
def get_db() -> Session:
    """
    Context manager برای دریافت session دیتابیس
    
    Usage:
        with get_db() as db:
            orders = db.query(Order).all()
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


def get_db_session() -> Session:
    """
    دریافت session برای استفاده دستی (باید close شود)
    
    Usage:
        db = get_db_session()
        try:
            orders = db.query(Order).all()
            db.commit()
        finally:
            db.close()
    """
    return SessionLocal()


if __name__ == "__main__":
    from app.common.log import console
    
    console.print(f"[cyan]Database URL: {DATABASE_URL}[/cyan]")
    console.print(f"[cyan]Database Path: {DATABASE_PATH.absolute()}[/cyan]")
    
    # ساخت جداول
    console.print("\n[cyan]Initializing database...[/cyan]")
    init_db()
    console.print("[green]✓ Database initialized successfully![/green]")
    
    # تست اتصال
    console.print("\n[cyan]Testing database connection...[/cyan]")
    with get_db() as db:
        console.print("[green]✓ Connection successful![/green]")
