import json, os

from dotenv import load_dotenv

load_dotenv()

# --- Получить из Github Secrets ---
# COOKIES_JSON = os.getenv('COOKIES_JSON')
# GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
# NINJAS_API_KEY = os.getenv('NINJAS_API_KEY')

# --- Для локальных тестов ---
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
NINJAS_API_KEY = os.environ.get('NINJAS_API_KEY', '')
COOKIES_JSON = os.environ.get('COOKIES_JSON', '{}')

cookies = json.loads(COOKIES_JSON)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "ru-RU,ru;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Cache-Control": "max-age=0",
    "sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="120"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
}

GROUP_ID = 352
MY_USER_ID = 8724
QUEUE_FILE = "queue.json"  # файл для сохранения очереди
FUNCTIONS_TEXT = [
    "/randomUser — выбор случайного пользователя из группы", 
    "/randomNum [число] — случайное число до между 1 и заданным вами числом (макс. 10-и значное)", 
    "/allUsers — список всех пользователей группы", 
    "/checkinfo [айди] — досье на пользователя по айди",
    "/quote — случайная цитата Стэтхема",
    "/duel [имя1] [имя2] — дуэль между двумя людьми",
    "/love [имя1] [имя2] — уровень совместимости двух людей",
    "/horoscope — гороскоп",
    "/decide — помогает принять решение. Да или нет",
    "/fact — случайный выдуманный факт",
    "/coin — подбрасывает монетку",
    "/translate [язык] [текст] — переводить текст на указанный язык. Пример использования: /translate en Привет -> Hello",
    "/city [название города] — получить данные о городе",
    "/about — о NVAi", 
    "/rules — правила группы", 
    "/help — список команд", 
    "@ [текст] — сгенерировать изображние"
]
FUNCTIONS_LIST = ["/RANDOMUSER", "/RANDOMNUM", "/ALLUSERS", "/ABOUT", "/RULES", "/HELP", "/CHECKINFO", "/QUOTE", "/DUEL", 
                  "/LOVE", "/HOROSCOPE", "/DECIDE", "/FACT", "/COIN", "/TRANSLATE", "/CITY"]