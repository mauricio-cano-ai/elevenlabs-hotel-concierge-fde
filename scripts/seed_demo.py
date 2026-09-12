from app.config import get_settings
from app.persistence.database import Database


if __name__ == "__main__":
    settings = get_settings()
    Database(settings.database_url)
    print(f"Demo database ready: {settings.database_url}")
