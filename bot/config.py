import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))
WEBAPP_URL = os.getenv("WEBAPP_URL", "")
SUPPORT_USERNAME = os.getenv("SUPPORT_USERNAME", "support")

# Пакеты звёзд для продажи
STAR_PACKAGES = [
    {"id": 1, "stars": 50, "price": 50, "bonus": 0},
    {"id": 2, "stars": 100, "price": 100, "bonus": 5},
    {"id": 3, "stars": 250, "price": 250, "bonus": 15},
    {"id": 4, "stars": 500, "price": 500, "bonus": 50},
    {"id": 5, "stars": 1000, "price": 1000, "bonus": 150},
    {"id": 6, "stars": 2500, "price": 2500, "bonus": 500},
]
