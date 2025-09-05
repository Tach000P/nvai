import json, os

# from dotenv import load_dotenv

# load_dotenv()

# --- Получить из Github Secrets ---
COOKIES_JSON = os.getenv('COOKIES_JSON')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')


# --- Для локальных тестов
# HG_API_KEY = os.environ.get('HG_API_KEY', '')
# COOKIES_JSON = os.environ.get('COOKIES_JSON', '{}')


cookies = json.loads(COOKIES_JSON)

GROUP_ID = 352
MY_USER_ID = 8724
QUEUE_FILE = "queue.json"  # файл для сохранения очереди
FUNCTIONS = ["/randomUser", "/randomNum", "/allUsers", "/about", "/rules", "/help",]