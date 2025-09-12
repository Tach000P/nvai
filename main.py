import requests
import time
import json
import os
from bs4 import BeautifulSoup
from model_rotator import model_rotator
from data import cookies, MY_USER_ID, GROUP_ID, FUNCTIONS_LIST, QUEUE_FILE
from functions import functions

headers = {
    "User-Agent": "Mozilla/5.0",
    "Referer": f"https://nolvoprosov.ru/groups/{GROUP_ID}",
}

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

# --- Основной цикл ---
while True:
    try:
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

            text_first_word = queue[i]["text"].split()[0] if queue[i]["text"].split() else ""
            text_second_word = queue[i]["text"].split()[1] if len(queue[i]["text"].split()) > 1 else ""

            if queue[i]["status"] == "pending":

                # --- Проверяем, функция ли это ---
                if text_first_word.upper() in FUNCTIONS_LIST:
                    reply = functions(text_first_word, text_second_word)

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

                time.sleep(1)

    except Exception as e:
        print("Ошибка в основном цикле:", e)
        time.sleep(5)
