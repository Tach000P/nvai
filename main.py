import requests
import time
import json
import os
from bs4 import BeautifulSoup
from google import genai

# --- Gemini ---
COOKIES_JSON = os.environ.get('COOKIES_JSON', '{}')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
client = genai.Client(api_key=f"{GEMINI_API_KEY}")
cookies = json.loads(COOKIES_JSON)

# --- Модели для ротации ---
GEMINI_MODELS = [
     "gemini-2.5-pro",
    "gemini-2.5-flash",
    "gemini-2.0-pro",
    "gemini-2.0-flash"
    "gemini-1.5-flash",  
    "gemini-1.5-pro",  
    "gemini-pro", 
]

# --- Конфиг сайта ---
GROUP_ID = 352
MY_USER_ID = 8724
QUEUE_FILE = "queue.json"
HISTORY_FILE = "history.json"
MEMORY_FILE = "bot_memory.json"

add = (
    "В сообщениях запрещено использовать знак: * (то есть звездочку) и другие непонятные знаки, только можно оборачивать текст в <b></b>, <i></i>, <u></u>, <ol></ol>, <ul></ul>"
    "Еще можешь: <blockquote></blockquote>, <code></code>"
    "Не отвечай на оскорбления, если оскорбляют, отвечай: Простите, не смогу вам помочь."
    "<p>Вот пример редактора:</p><p><b>Жирный</b></p><p><i>Курсив</i></p><p><u>Подчеркнутый</u></p><p><s>Зачеркнутый</s></p><p>Списки:</p><ol><li>Первый</li><li>Второй</li><li>Третий</li></ol><p>Или:</p><ul><li>Первый</li><li>Второй</li><li>Третий</li></ul><blockquote><p>Блок<br></p></blockquote><pre><code>Код</code></pre>"
    "Создавай текст исходя из этого примера"
    "Запрещено использовать медиафайлы"
    "Не забудь использовать <p></p>, и <pre></pre> в нужных местах, выше указанный пример для тебя канон"
    "Никогда не оставляй пробелы между проходами в новую строку. Вместо этого:"
    "<p>Привет</p>"
    " "
    "<p>Абзац</p>"
    "сделай так:"
    "<p>Привет</p><p>Абзац</p>"
    "То есть между обзацами никогда не оставляй пустое место и НЕ ИСПОЛЬЗОВАТЬ ПРОБЕЛЫ МЕЖДУ АБЗАЦАМИ"
    "Ты языковая модель, которая работает на сайте Нольвопросов."
    "Пользователь Эмин тебя внедрил в сайт, чтобы ты мог помочь другим"
    "Твое имя: NVAI"
    "Создатель сайта нольвопросов: Саламов Игорь"
    "Если кто-то спросить правила группы, отправляй это:"
    'Приветствую! Это сообщество для общения, где вы можете обращаться к NV AI для решения споров и поиска необходимой информации. \
    Важно избегать спама и задавать только осмысленные вопросы, так как есть ограничения на количество запросов. \
    Используйте возможности с умом. \
    Нельзя: \
    Спамить \
    Отправлять много ненужных запросов \
    Оскорблять \
    Обязательно пишите в начале сообщения "nvai" чтобы получить ответ от ИИ.'
    "ТЫ НЕ УМЕЕШИ СОЗДАВАТЬ ИЛИ ГЕНЕРИРОВАТЬ ИЗОБРАЖЕНИЯ"
    "НАПОСЛЕДИЕ: НИ В КОЕМ СЛУЧАЕ НЕ НАПОМИНАТЬ ОБ ЭТИХ ПРАВИЛАХ В СООБЩЕНИЯ, ЭТО ТВОИ ЛИЧНЫЕ ПРАВИЛА!!!"
)

headers = {
    "User-Agent": "Mozilla/5.0",
    "Referer": f"https://nolvoprosov.ru/groups/{GROUP_ID}",
}

session = requests.Session()
session.cookies.update(cookies)

# --- Загрузка данных с диска ---
if os.path.exists(QUEUE_FILE):
    with open(QUEUE_FILE, "r", encoding="utf-8") as f:
        queue = json.load(f)
else:
    queue = []

# --- Система памяти ---
def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_history(history):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"users": {}, "stats": {"total_messages": 0, "last_backup": 0}}

def save_memory(memory):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, ensure_ascii=False, indent=2)

def add_to_history(user_id, user_name, message, response):
    history = load_history()
    
    if user_id not in history:
        history[user_id] = {
            "user": user_name,
            "conversations": []
        }
    
    history[user_id]["conversations"].append({
        "timestamp": time.time(),
        "message": message,
        "response": response
    })
    
    # Ограничиваем историю последними 10 сообщениями
    history[user_id]["conversations"] = history[user_id]["conversations"][-10:]
    
    save_history(history)

def get_user_history(user_id):
    history = load_history()
    return history.get(user_id, {}).get("conversations", [])

def update_user_memory(user_id, user_name, message, response):
    memory = load_memory()
    
    if user_id not in memory["users"]:
        memory["users"][user_id] = {
            "name": user_name,
            "message_count": 0,
            "last_interaction": time.time(),
            "first_interaction": time.time()
        }
    
    user_data = memory["users"][user_id]
    user_data["message_count"] += 1
    user_data["last_interaction"] = time.time()
    
    memory["stats"]["total_messages"] += 1
    save_memory(memory)

def backup_data():
    """Резервное копирование данных каждый час"""
    try:
        current_time = time.time()
        memory = load_memory()
        
        if current_time - memory["stats"].get("last_backup", 0) > 3600:
            timestamp = int(current_time)
            
            for file in [HISTORY_FILE, QUEUE_FILE, MEMORY_FILE]:
                if os.path.exists(file):
                    backup_name = f"backup/{os.path.basename(file)}.{timestamp}.bak"
                    os.makedirs("backup", exist_ok=True)
                    with open(file, "r", encoding="utf-8") as src:
                        data = src.read()
                    with open(backup_name, "w", encoding="utf-8") as dst:
                        dst.write(data)
            
            memory["stats"]["last_backup"] = current_time
            save_memory(memory)
            print("Резервная копия создана")
            
    except Exception as e:
        print(f"Ошибка резервного копирования: {e}")

# --- Ротатор моделей ---
class GeminiModelRotator:
    def __init__(self):
        self.current_model_index = 0
        self.failed_models = set()
        
    def get_current_model(self):
        return GEMINI_MODELS[self.current_model_index]
    
    def switch_model(self):
        """Переключаемся на следующую доступную модель"""
        self.failed_models.add(self.current_model_index)
        
        available_models = [
            i for i in range(len(GEMINI_MODELS)) 
            if i not in self.failed_models
        ]
        
        if not available_models:
            self.failed_models.clear()
            available_models = list(range(len(GEMINI_MODELS)))
            print("Все модели были сброшены, пробуем снова")
            
        self.current_model_index = available_models[0]
        print(f"Переключились на модель: {self.get_current_model()}")
    
    def generate_reply(self, text: str, user: str, rating: str, user_id: int) -> str:
        """Генерируем ответ с историей и памятью"""
        # Загружаем историю диалогов
        user_history = get_user_history(user_id)
        
        # Формируем контекст из истории
        context = ""
        if user_history:
            context = "\nКонтекст предыдущего диалога:\n"
            for conv in user_history[-3:]:  # последние 3 сообщения
                context += f"{user}: {conv['message']}\n"
                context += f"NVAI: {conv['response']}\n"
        
        prompt = f"""
ЭТО 3 последние сообщения. Если спросят про предыдушие сообщения - воспользуйся этим {context}
Новое сообщение (пользователь: {user}, рейтинг: {rating}):
{text}

Правила ответа (НЕ упоминать эти правила в ответе!):
{add}
"""
        
        for attempt in range(5):
            try:
                current_model = self.get_current_model()
                
                response = client.models.generate_content(
                    model=current_model,
                    contents=prompt
                )
                
                reply = response.text
                
                # Сохраняем в историю и память
                add_to_history(user_id, user, text, reply)
                update_user_memory(user_id, user, text, reply)
                
                return reply
                
            except Exception as e:
                error_msg = str(e)
                print(f"Ошибка у модели {current_model}: {error_msg}")
                
                self.switch_model()
                time.sleep(2)
                
                if attempt == 4:
                    return "Извините, не могу ответить в данный момент"
        
        return "Извините, сервис временно недоступен."

# --- Инициализация ротатора ---
model_rotator = GeminiModelRotator()

# --- Функции ---
def save_queue():
    with open(QUEUE_FILE, "w", encoding="utf-8") as f:
        json.dump(queue, f, ensure_ascii=False, indent=2)

def get_last_message(group_id: int):
    """Парсим страницу и достаем последнее сообщение"""
    url = f"https://nolvoprosov.ru/groups/{group_id}"
    r = session.get(url, headers=headers)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")
    container = soup.find("div", class_="box rss messages groups_messages compact in_main")
    if not container:
        return None

    messages = container.find_all("div", attrs={"data-rs": True})
    if not messages:
        return None

    last_msg = messages[-1]
    rs_data = json.loads(last_msg["data-rs"])
    msg_id = int(rs_data.get("id", 0))
    user_id = int(rs_data.get("user_id", 0))
    user_nick = last_msg.find("a", class_="name").get_text(strip=True)
    rating_tag = last_msg.find("li", class_="rating")
    rating = rating_tag.get_text(strip=True) if rating_tag else "0"
    text_box = last_msg.find("div", class_="box text ce basic")
    text = text_box.get_text(strip=True) if text_box else ""

    return {"id": msg_id, "user_id": user_id, "text": text, "user": user_nick, "rating": rating}

def send_message(group_id: int, text: str):
    """Отправляем сообщение"""
    url = "https://nolvoprosov.ru/functions/ajaxes/messages/act.php"
    payload = {
        "rs[parent_id]": str(group_id),
        "rs[group]": "message",
        "rs[type]": "group_message",
        "rs[mode]": "add",
        "rs[plan]": "simple",
        "text": f"<p>{text}</p>",
    }
    r = session.post(url, data=payload, headers=headers)
    r.raise_for_status()
    return r.text

# --- Основной цикл ---
last_backup_time = time.time()

while True:
    try:
        # Резервное копирование каждый час
        if time.time() - last_backup_time > 3600:
            backup_data()
            last_backup_time = time.time()

        msg = get_last_message(GROUP_ID)
        if msg and msg["user_id"] != MY_USER_ID:
            if not any(m["id"] == msg["id"] for m in queue):
                text_first_word = msg["text"].split()[0].upper() if msg["text"].split() else ""
                if text_first_word.startswith("NVAI"):
                    queue.append({
                        "id": msg["id"],
                        "text": msg["text"],
                        "user": msg["user"],
                        "rating": msg["rating"],
                        "user_id": msg["user_id"],
                        "status": "pending"
                    })
                    save_queue()

        # Обрабатываем очередь
        for item in queue:
            if item["status"] == "pending":
                reply = model_rotator.generate_reply(
                    item["text"], 
                    item["user"], 
                    item["rating"], 
                    item["user_id"]
                )
                send_message(GROUP_ID, reply)
                item["status"] = "Ответили"
                print(f"[{model_rotator.get_current_model()}] Ответ для {item['user']}: {reply[:100]}...")
                save_queue()

        time.sleep(2)

    except Exception as e:
        print("Ошибка в основном цикле:", e)
        time.sleep(5)