import os
from dotenv import load_dotenv

from app.config import Settings


def get_settings() -> Settings:
    load_dotenv()
    return Settings(
        control_env=os.getenv("CONTROL_ENV", "dev"),
        database_url=os.getenv("DATABASE_URL", "sqlite:///./control.sqlite3"),
        manamod_username=os.getenv("MANAMOD_USERNAME"),
        manamod_password=os.getenv("MANAMOD_PASSWORD"),
        mihanstore_username=os.getenv("MIHANSTORE_USERNAME"),
        mihanstore_password=os.getenv("MIHANSTORE_PASSWORD"),
        memarket_username=os.getenv("MEMARKET_USERNAME"),
        memarket_password=os.getenv("MEMARKET_PASSWORD"),
    )
