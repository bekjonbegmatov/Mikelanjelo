import os
from dotenv import load_dotenv

# Загрузка переменных из .env файла
load_dotenv()

TELEGRAM_API_KEY = os.getenv("TELEGRAM_API_KEY")
GEO_API_KEY = os.getenv("GEO_API_KEY")