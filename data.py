import json, os

# from dotenv import load_dotenv

# load_dotenv()

# --- Получить из Github Secrets ---
COOKIES_JSON = os.getenv('COOKIES_JSON')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
NINJAS_API_KEY = os.getenv('NINJAS_API_KEY')

# --- Для локальных тестов ---
# GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
# NINJAS_API_KEY = os.environ.get('NINJAS_API_KEY', '')
# COOKIES_JSON = os.environ.get('COOKIES_JSON', '{}')

cookies = json.loads(COOKIES_JSON)

GROUP_ID = 352
MY_USER_ID = 8724
QUEUE_FILE = "queue.json"  # файл для сохранения очереди
FUNCTIONS_TEXT = [
    "/randomUser — выбор случайного пользователя из группы", 
    "/randomNum [число] — случайное число до между 1 и заданным вами числом (макс. 10-и значное)", 
    "/allUsers — список всех пользователей группы", 
    "/checkinfo [айди] — досье на пользователя по айди"
    "/quote — случайная цитата Стэтхема"
    "/duel [имя1] [имя2] — дуэль между двумя людьми"
    "/love [имя1] [имя2] — уровень совместимости двух людей"
    "/horoscope — гороскоп"
    "/decide — помогает принять решение. Да или нет"
    "/fact — случайный выдуманный факт"
    "/coin — подбрасывает монетку"
    "/translate [язык] [текст] — переводить текст на указанный язык. Пример использования: /translate en Привет -> Hello"
    "/city [название города] — получить данные о городе"
    "/about — о NVAi", 
    "/rules — правила группы", 
    "/help — список команд", 
    "@ [текст] — сгенерировать изображние"
]
FUNCTIONS_LIST = ["/RANDOMUSER", "/RANDOMNUM", "/ALLUSERS", "/ABOUT", "/RULES", "/HELP", "/CHECKINFO", "/QUOTE", "/DUEL", 
                  "/LOVE", "/HOROSCOPE", "/DECIDE", "/FACT", "/COIN", "/TRANSLATE", "/CITY"
                  ]