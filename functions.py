from data import GROUP_ID, cookies, FUNCTIONS
from bs4 import BeautifulSoup
import requests
import os
import random

url_members = f"https://nolvoprosov.ru/groups/{GROUP_ID}/members"
url_rules = f"https://nolvoprosov.ru/groups/{GROUP_ID}/rules"

headers = {
    "User-Agent": "Mozilla/5.0",
    "Referer": url_members,
}

session = requests.Session()
session.cookies.update(cookies)

functions_descriptions = [
    "выбор случайного пользователя из группы",
    "случайное число до между 1 и заданным вами числом (макс. 10-и значное)",
    "список всех пользователей группы",
    "о NVAi",
    "правила группы",
    "список команд"
]

def get_as_text_array(a):

    l = []

    for i in range(1, len(a)):
        l.append(a[i].text)

    return l

def get_all_users(t: str):
    """Парсим страницу и достаем список пользователей"""
    r = session.get(url_members, headers=headers)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, 'html.parser')

    container = soup.find('table', class_="box rss groups_users tb_list headers")

    users = container.find_all('div', class_="tb header mini", attrs={"data-rs": True})

    roles = container.find_all('td', class_="role")

    roles.pop(0)

    names = get_as_text_array(users)

    roles_text = get_as_text_array(roles)

    if t == "names":
        return names
    elif t == "roles":
        return roles_text

def functions(f: str, c: str):

    if f == "/randomUser":

        names = get_all_users("names")
        
        random_user = random.choice(names)

        return random_user
    
    elif f == "/allUsers":

        names = get_all_users("names")
        roles = get_all_users("roles")

        result = []

        for i in range(0, len(names)):
            result.append(f"<li><b>{names[i]}</b> — {roles[i]}</li>")

        return f"<blockquote>Все пользователи группы:</blockquote><ol>{''.join(result)}</ol>"
    
    elif f == "/randomNum":

        num = int(c)

        if len(c) > 10:
            return "Слишком большое число. Максимум 10-и значное."
        try:
            return str(random.randint(1, num))
        except:
            return "Отправьте число для рандомного выбора: /randomNum *число*"

    elif f == "/help":

        commands = []

        for i in range(1, len(FUNCTIONS)):
            commands.append(f"<li>{FUNCTIONS[i]} — {functions_descriptions[i]}</li>")

        return(
            "Все конманды:"
            "<ul>"
                f"{''.join(commands)}"
                "<li>/ — ответ от стандартного ИИ</li>"
                "<li>// — ответ от умного ИИ</li>"
                "<li>/// — ответ от самого продвинутого ИИ</li>"
            "</ul>"
        )
        
    elif f == "/about":
        return(
            "<p><b>Информация о NVAi:</b></p>"
            "<p>NVAi — это интеллектуальный чат-бот, созданный для развлечения и "
            "упрощения взаимодействия с искусственным интеллектом через группы на "
            "сайте «Нольвопросов». Этот бот разработан пользователем Эмин и предоставляет "
            "пользователям возможность быстро получать ответы на вопросы, находить полезную информацию "
            "и даже развлекаться, играя с ним.</p>"
            "Это обычный чат-бот, который может помочь вам быстро решить вопросы, найти информацию или просто "
            "поиграть с вами в игры.</p>"
            "<p>Чтобы узнать все доступные команды и их функции, введите команду <b>/help</b> в чат. "
            "Бот предоставит вам список команд и краткое описание каждой из них.</p>"
            "<p>Чтобы ознокомиться с правилами группы вызовите команду <b>/rules</b></p>"
            "<p><b>Обращение к разработчику:</b></p>"
            "<p>Если у вас возникли вопросы, предложения или вы хотите получить более высокий статус, "
            "свяжитесь с разработчиком бота, Эмин. Для этого перейдите по ссылке:https://nolvoprosov.ru/users/7282</p>"
        )

    elif f == "/rules":
        """Парсим страницу и достаем правила"""
        r = session.get(url_rules, headers=headers)
        r.raise_for_status()

        soup = BeautifulSoup(r.text, 'html.parser')

        container = soup.find('div', class_="box basic text ce")

        tags = []

        for i in range(0, len(container.contents)):
            tags.append(f"{container.contents[i]}")
        
        return f"{''.join(tags)}"