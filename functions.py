from data import GROUP_ID, cookies, FUNCTIONS_TEXT
from bs4 import BeautifulSoup
import os, json, random, requests, asyncio
from google import genai
from data import GEMINI_API_KEY, NINJAS_API_KEY
from google.genai import types
from mems import *
from rules import rules
from googletrans import Translator

client = genai.Client(api_key=f"{GEMINI_API_KEY}")

answers_config = types.GenerateContentConfig(
    system_instruction="Проанализируй ответы пользователя и создай смешную шуточную фразу в третьем лице, которая обыграет его стиль общения/темы. Избегай общих фраз — только конкретика и юмор based на его ответах. Маты разрешены"
)

questions_config = types.GenerateContentConfig(
    system_instruction="Проанализируй вопросы пользователя и создай шуточную фразу в третьем лице. Не пытайся задеть его - просто фраза с сарказмом в шуточном стиле. Маты разрешены"
)

hidden_talent_config = types.GenerateContentConfig(
    system_instruction="Создай очень короткую фразу о скрытом таланте пользователя, исходя от его вопросов и ответов. Фраза должна быть шуточным"
)

toxic_config = types.GenerateContentConfig(
    system_instruction="предложением, который состоит не более из пяти слов, описуй его токсичность ответов. Шутки, сарказм и маты разрешены"
)

duel_config = types.GenerateContentConfig(
    system_instruction="Сделать дуэль между двумя людьми, имена которых заданы в начале текста и придумать абсурдную причину победы одного, поражения или ничьи. В дуэле должны быть раунды, тоже шуточные и абсурдные, конечно, но эпичные, с действиями и желательно с боями. Сарказм, маты и шутки разрешены. ВАЖНО: Не упоминать про абсурдность в тексте"
)

love_config = types.GenerateContentConfig(
    system_instruction="Ты должен создать краткое объяснение, почему 2 человека подходят или не подходят друг к другу, и определить уровень совместимости. Можешь придумать что угодно, главное - смешное и мемное. Сарказм и маты разрешены. ВАЖНО: укажи уровень совместимости и почему именно столько"
)

horoscope_config = types.GenerateContentConfig(
    system_instruction="Выдать абсурдное предсказание на день, никак не связанное с реальностью. Сарказм, черный юмор и маты разрешены"
)

fact_config = types.GenerateContentConfig(
    system_instruction="100% выдуманный, но правдоподобно звучащий факт. Сарказм, маты, черный юмор - разрешены"
)

user_agent = "Mozilla/5.0"

session = requests.Session()
session.cookies.update(cookies)

async def translate(text: str, src="ru", dest="en"):
    try:
        async with Translator() as translator:
            result = await translator.translate(text, dest=dest)
            return result.text
    except Exception as e:
        print(e)
        return "Выберите доступный язык"

def get_as_text_array(a):

    l = []

    for i in range(1, len(a)):
        l.append(a[i].text)

    return l

def generate_text(content, config): 
    output = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=content,
        config=config
    )

    return output.text

def get_answers(id):
    url_user = f"https://nolvoprosov.ru/users/{id}/questions/answers"

    headers = {
        "User-Agent": user_agent,
        "Referer": url_user,
    }

    r = session.get(url_user, headers=headers)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, 'html.parser')

    container = soup.find("div", class_="box rss answers questions_answers compact")    

    answers = container.find_all("div", class_="box text basic")

    answers_text = get_as_text_array(answers)

    return answers_text

def get_questions(id):
    url_user = f"https://nolvoprosov.ru/users/{id}/questions"

    headers = {
        "User-Agent": user_agent,
        "Referer": url_user,
    }

    r = session.get(url_user, headers=headers)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, 'html.parser')

    container = soup.find("div", class_="box rss bases questions list")    

    questions = container.find_all("a", class_="text m")

    questions_text = get_as_text_array(questions)

    return questions_text

def get_profile(id: str):

    url_user = f"https://nolvoprosov.ru/users/{id}"

    headers = {
        "User-Agent": user_agent,
        "Referer": url_user,
    }

    r = session.get(url_user, headers=headers)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, 'html.parser')

    profile = soup.find("div", class_="rs user")

    return profile

def get_all_users(t: str):
    """Парсим страницу и достаем список пользователей"""

    url_members = f"https://nolvoprosov.ru/groups/{GROUP_ID}/members"

    headers = {
        "User-Agent": user_agent,
        "Referer": url_members,
    }

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
    
#-----------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------
#
#                                        ВСЕ ФУНКЦИИ 
#
#-----------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------


def functions(f: str, c1="", c2="", text1="", text2="", text3=""):

    if f == "/RANDOMUSER":

        names = get_all_users("names")
        
        random_user = random.choice(names)

        return random_user
    
    elif f == "/ALLUSERS":

        names = get_all_users("names")
        roles = get_all_users("roles")

        result = []

        for i in range(0, len(names)):
            result.append(f"<li><b>{names[i]}</b> — {roles[i]}</li>")

        return f"<blockquote>Все пользователи группы:</blockquote><ol>{''.join(result)}</ol>"
    
    elif f == "/RANDOMNUM":

        num = int(c1)

        if len(c1) > 10:
            return "Слишком большое число. Максимум 10-и значное."
        try:
            return str(random.randint(1, num))
        except:
            return "Отправьте число для рандомного выбора: /randomNum [число]"

    elif f == "/HELP":

        commands = []

        for i in range(1, len(FUNCTIONS_TEXT)):
            commands.append(f"<li>{FUNCTIONS_TEXT[i]}</li>")

        return(
            "Все конманды:"
            "<ul>"
                f"{''.join(commands)}"
                "<li>/ — ответ от стандартного ИИ</li>"
                "<li>// — ответ от умного ИИ</li>"
            "</ul>"
        )
        
    elif f == "/ABOUT":
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

    elif f == "/RULES":
        """Парсим страницу и достаем правила"""

        url_rules = f"https://nolvoprosov.ru/groups/{GROUP_ID}/rules"

        headers = {
            "User-Agent": user_agent,
            "Referer": url_rules,
        }

        r = session.get(url_rules, headers=headers)
        r.raise_for_status()

        soup = BeautifulSoup(r.text, 'html.parser')

        container = soup.find('div', class_="box basic text ce")

        tags = []

        for i in range(0, len(container.contents)):
            tags.append(f"{container.contents[i]}")
        
        return f"{''.join(tags)}"
    
    elif f == "/CHECKINFO":

        """Проверяем, не админ ли это"""
        if c1 == "7282":
            return "Аднима не трогаем!"
        elif not c1:
            return "Пожалуйста, укажите айди. /checkingo [айди]"

        """Достаем информацию из профила"""

        try:
            profile = get_profile(id=c1)

            name = profile.find("div", class_="name").text
            isOnline = profile.find("span", class_="has_online").text
            rating = profile.find("div", class_="place").find("span", class_="val").text
            
            if isOnline == "На сайте":
                isOnline = "Да"
            else:
                isOnline = "Нет"

            """Проверяем уровень токсичности ответов"""

            answers = get_answers(c1)

            if not answers:
                answers_content = "Дебил без ответов, нечего проверят"
            else:
                answers_content = "\n".join(answers)

            answers_type = generate_text(content=answers_content, config=answers_config)

            """Провряем какого типа вопросы задается пользователем"""

            questions = get_questions(id=c1)

            if not questions:
                questions_content = "Нет вопросов длч оценки. Серьезно?"
            else:
                questions_content = "\n".join(questions)

            questions_type = generate_text(content=questions_content, config=questions_config)

            """Создаем *скрытый талант* анализируя вопросы и ответы"""

            hidden_talent = generate_text(content=[answers_content, questions_content], config=hidden_talent_config)

            """Проверяем уровень токсичности ответов"""

            toxicity = generate_text(content=answers_content, config=toxic_config)

            result = f"""
                <b>ДОСЬЕ НА {name}</b>
                <ol>
                    <li><b>Онлайн:</b> {isOnline}</li>
                    <li><b>Место в рейтинге:</b> {rating}</li>
                    <li><b>Тип ответов:</b> {answers_type}</li>
                    <li><b>Тип вопросов:</b> {questions_type}</li>
                    <li><b>Любимый вид пельменей:</b> {random.choice(pelmeni_jokes)}</li>
                    <li><b>IQ по версии кота:</b> {random.randint(70, 140)}</li>
                    <li><b>Скрытый талант:</b> {hidden_talent}</li>
                    <li><b>Уровень токсичности:</b> {toxicity}</li>
                </ol>
            """

            return result
        
        except Exception as e:

            error_msg = str(e)

            if "404" in error_msg:
                return "Такого пользователя не существует"
            else:
                return "Что-то пошло не так"
    
    elif f == "/QUOTE":
        return f"<blockquote>{random.choice(statham_quotes)}</blockquote>"
    
    elif f == "/DUEL":

        if not c1 or not c2:
            return "Пожалуйста, укажите имена. /duel [имя1] [имя2]"
       
        result = generate_text(content=[f"Имя 1:{c1} Имя 2:{c2}", rules], config=duel_config)
        
        return result
    
    elif f == "/LOVE":

        if not c1 or not c2:
            return "Пожалуйста, укажите имена. /love [имя1] [имя2]"

        result = generate_text(content=[f"Имя 1:{c1} Имя 2:{c2}", rules], config=love_config)

        return result
    
    elif f == "/HOROSCOPE":

        result = generate_text(content="", config=horoscope_config)

        return result
    
    elif f == "/DECIDE":
        return decision_responses[random.randint(0, 2)][random.randint(0, 9)]
    
    elif f == "/FACT":

        result = generate_text(content="", config=fact_config)

        return result
    
    elif f == "/COIN":

        n = random.randint(0, 1)

        coin = [
            "https://storage.yandexcloud.net/nv1/images/2025/09/13/5671c93acc69e4c7e920c4c965f0481d.jpg",
            "https://storage.yandexcloud.net/nv1/images/2025/09/13/01981559834be5bd1d64841f4d8dfccc.jpg"
        ]

        return f'<img src="{coin[n]}" />'
    
    elif f == "/TRANSLATE":

        if not text2:
            return "Отправьте текст"
        else:
            return asyncio.run(translate(text=text2, dest=c1))
    
    elif f == "/CITY":

        api_url = f'https://api.api-ninjas.com/v1/city?name={c1}'
        response = requests.get(api_url, headers={'X-Api-Key': NINJAS_API_KEY})

        if response.status_code == requests.codes.ok:
            info = json.loads(response.text)[0]
            is_capital = "Да" if info["is_capital"] else "Нет"
            return f"""
                ╔═══════════════════════════════════════════════════════╗
                ╟─────────────────── ГОРОДСКАЯ КАРТОЧКА ────────────────╢
                ║ • 🏙️  Название: {info["name"]}
                ║ • 🗺️  Координаты: {info["latitude"]}, {info["longitude"]}
                ║ • 🌎  Страна: {info["country"]}
                ║ • 👥  Население: {info["population"]}
                ║ • 👑  Столица: {is_capital}
                ║ • 📍  Регион: {info["region"]}
                ╚═══════════════════════════════════════════════════════╝
            """
        else:
            print("Error:", response.status_code, response.text)
            return response.text