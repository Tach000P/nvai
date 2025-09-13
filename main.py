import requests, time, json, os, random, time
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from model_rotator import model_rotator
from data import *
from functions import functions

session = requests.Session()
session.cookies.update(cookies)

# --- Загрузка очереди с диска ---
if os.path.exists(QUEUE_FILE):
    with open(QUEUE_FILE, "r", encoding="utf-8") as f:
        queue = json.load(f)
else:
    queue = []

# --- Функции ---
def save_queue():
    with open(QUEUE_FILE, "w", encoding="utf-8") as f:
        json.dump(queue, f, ensure_ascii=False, indent=2)


def get_last_message(group_id: int):
    """Парсим страницу и достаем последнее сообщение с максимальным контекстом"""
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

    # Получаем последнее сообщение
    last_msg = messages[-1]
    rs_data = json.loads(last_msg["data-rs"])
    msg_id = int(rs_data.get("id", 0))
    user_id = int(rs_data.get("user_id", 0))
    
    # Если это наше сообщение - пропускаем
    if user_id == MY_USER_ID:
        return None

    user_nick = last_msg.find("a", class_="name").get_text(strip=True)
    rating_tag = last_msg.find("li", class_="rating")
    rating = rating_tag.get_text(strip=True) if rating_tag else "0"
    text_box = last_msg.find("div", class_="box text ce basic")
    text = text_box.get_text(strip=True) if text_box else ""

    # Получаем ВЕСЬ контекст чата (последние 40 сообщений)
    chat_context = []
    for msg in messages[-40:]:  # последние 40 сообщений чата
        try:
            msg_data = json.loads(msg["data-rs"])
            msg_user_id = msg_data.get("user_id", 0)
            msg_user = msg.find("a", class_="name")
            msg_user_name = msg_user.get_text(strip=True) if msg_user else "Unknown"
            
            msg_text = msg.find("div", class_="box text ce basic")
            if msg_text:
                chat_context.append({
                    "user_id": msg_user_id,
                    "user": msg_user_name,
                    "text": msg_text.get_text(strip=True),
                    "is_ai": msg_user_id == MY_USER_ID,
                    "timestamp": msg_data.get("id", 0)
                })
        except Exception as e:
            print(f"Ошибка парсинга сообщения: {e}")
            continue

    return {
        "id": msg_id, 
        "text": text, 
        "user": user_nick, 
        "rating": rating, 
        "context": chat_context,
        "user_context": [m for m in chat_context if m["user_id"] == user_id][-20:],
        "user_id": f"{user_id}"
    }


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

def get_sleep_until_7am():
    now = datetime.now()
    # Вычисляем время до 7:00 следующего дня
    tomorrow_7am = now.replace(hour=7, minute=0, second=0, microsecond=0)
    sleep_seconds = (tomorrow_7am - now).total_seconds()
    return max(sleep_seconds, 0)  # Не меньше 0

def should_skip_night():
    now = datetime.now()
    # Если время между 1:57 и 7:00
    return now.hour >= 1 and now.minute >= 57 and now.hour < 7

# --- Основной цикл ---
while True:
    try:

        if should_skip_night():
            send_message(GROUP_ID, "🌙 Бот спит до 7:00")
            exit(0)
            time.sleep(600)
            continue

        msg = get_last_message(GROUP_ID)

        if msg and msg["user_id"] != MY_USER_ID:

            if not any(m["id"] == msg["id"] for m in queue):

                text_first_word = msg["text"].split()[0].upper() if msg["text"].split() else ""

                reply_type = "detailed" if text_first_word.startswith("//") else "standard"

                if text_first_word.startswith("/"):
                    queue.append({
                        "id": msg["id"],
                        "text": msg["text"],
                        "user": msg["user"],
                        "rating": msg["rating"],
                        "context": msg["context"],
                        "user_context": msg["user_context"],
                        "user_id": msg["user_id"],
                        "status": "pending",
                        "type": reply_type
                    })
                    save_queue()

        max_queue_size = 20  # Максимальный размер очереди

        for i in range(len(queue) - 1, -1, -1):

            text = queue[i]["text"]
            text_s = text.split()
            length = len(text_s)

            command = text_s[0] if text_s else ""
            text_first_word = text_s[1] if length > 1 else ""
            text_second_word = text_s[2] if length > 2 else ""

            # Правильное получение текста без N первых слов
            full_text_without_first_command = " ".join(text_s[1:]) if length > 1 else ""
            full_text_without_two_commands = " ".join(text_s[2:]) if length > 2 else ""  
            full_text_without_three_commands = " ".join(text_s[3:]) if length > 3 else ""

            if queue[i]["status"] == "pending":
                if command.upper() in FUNCTIONS_LIST:
                    reply = functions(
                        f=command.upper(), 
                        c1=text_first_word, 
                        c2=text_second_word, 
                        text1=full_text_without_first_command,
                        text2=full_text_without_two_commands,
                        text3=full_text_without_three_commands 
                    )

                else:
                # --- ГЕНЕРИРУЕМ ОТВЕТ ---
                    reply = model_rotator.generate_reply(
                        queue[i]["text"], queue[i]["user"], queue[i]["rating"],
                        queue[i]["context"], queue[i]["user_context"], str(queue[i]["user_id"]), queue[i]["type"]
                    )

                # --- ОТПРАВЛЯЕМ В ГРУППУ ---
                send_message(GROUP_ID, reply)
                print(f"[AI ответил]: {reply[:100]}...")
                queue[i]["status"] = "ответили"
                save_queue()
            
            # Удаляем старые сообщения если очередь слишком большая
            elif len(queue) > max_queue_size:
                del queue[0]  # Удаляем самое старое сообщение
                save_queue()

        time.sleep(random.randint(2, 5))

    except Exception as e:
        print("Ошибка в основном цикле:", e)
        time.sleep(5)
