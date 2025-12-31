from pydantic import BaseModel

class Settings(BaseModel):
    control_env: str = "dev"
    database_url: str = "sqlite:///./control.sqlite3"

    manamod_username: str | None = None
    manamod_password: str | None = None

    mihanstore_username: str | None = None
    mihanstore_password: str | None = None

    memarket_username: str | None = None
    memarket_password: str | None = None
