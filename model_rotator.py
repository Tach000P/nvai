import time, os
# from huggingface_hub import InferenceClient
from rules import rules
from data import GEMINI_API_KEY
from google import genai
from google.genai import types

# --- Gemini ---
# GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
client = genai.Client(api_key=f"{GEMINI_API_KEY}")

grounding_tool = types.Tool(
    google_search=types.GoogleSearch()
)

config = types.GenerateContentConfig(
    tools=[grounding_tool]
)

VIP_USERS = ("7282")

PREMIUM_USERS = VIP_USERS + ("")

class ModelRotator:


    def __init__(self):
        self.current_model_index_standard = 0
        self.current_model_index_premium = 0
        self.current_model_index_vip = 0
        self.failed_models_standard = set()
        self.failed_models_premium = set()
        self.failed_models_vip = set()
        
        # Модели в порядке приоритета
        self.VIP_MODELS = [
            "gemini-2.5-pro",
        ]
        
        self.PREMIUM_MODELS = [
            "gemini-2.0-pro",
            "gemini-2.5-flash",
            "gemini-1.5-pro" ,
        ]
        
        self.STANDARD_MODELS = [
            "gemini-2.0-flash",
            "gemini-1.5-flash",
        ]

    def get_vip_model(self):
        """Для VIP запросов"""
        return self.VIP_MODELS[self.current_model_index_vip]
    
    def get_premium_model(self):
        """Для премиум запросов"""
        return self.PREMIUM_MODELS[self.current_model_index_premium]
    
    def get_standard_model(self):
        """Для обычных запросов"""
        return self.STANDARD_MODELS[self.current_model_index_standard]
    
    def switch_model(self, model):
        """Переключает все ротаторы одновременно"""
        if model in self.STANDARD_MODELS:
            self.failed_models_standard.add(self.current_model_index_standard)
        
            available_indices_s = [
                i for i in range(len(self.STANDARD_MODELS))
                if i not in self.failed_models_standard
            ]
        
            if not available_indices_s:
                self.failed_models_standard.clear()
                available_indices_s = list(range(len(self.STANDARD_MODELS)))
                print("Все модели Standard сброшены")
            
            self.current_model_index_standard = available_indices_s[0]

        elif model in self.PREMIUM_MODELS:
            self.failed_models_premium.add(self.current_model_index_premium)
        
            available_indices_p = [
                i for i in range(len(self.PREMIUM_MODELS))
                if i not in self.failed_models_premium
            ]
        
            if not available_indices_p:
                self.failed_models_premium.clear()
                available_indices_p = list(range(len(self.PREMIUM_MODELS)))
                print("Все модели Premium сброшены")
            
            self.current_model_index_premium = available_indices_p[0]

        else:
            self.failed_models_vip.add(self.current_model_index_vip)
        
            available_indices_v = [
                i for i in range(len(self.VIP_MODELS))
                if i not in self.failed_models_vip
            ]
        
            if not available_indices_v:
                self.failed_models_vip.clear()
                available_indices_v = list(range(len(self.VIP_MODELS)))
                print("Все модели Vip сброшены")
            
            self.current_model_index_vip = available_indices_v[0]

    def generate_reply(self, text: str, user: str, rating: str, context: list, user_context: list, user_id: str, reply_type: str) -> str:
        """Генерация ответа"""
        context_str = "Контекст чата (последние сообщения):\n"
        for msg in context[-40:]:
            sender = "NVAI" if msg["is_ai"] else msg["user"]
            context_str += f"{sender}: {msg['text']}\n"
        
        user_history_str = "История сообщений этого пользователя:\n"
        for msg in user_context[-10:]:
            user_history_str += f"{user}: {msg['text']}\n"

        if user_id == "7282":
            user_status = "Admin"
        else:
            user_status = "User"
        
        prompt = f"""
            ID=({user_id})
            Status=({user_status})
            контекст: {context_str}
            история пользователя: {user_history_str}
            Новое сообщение (пользователь: {user}, рейтинг: {rating}):
            {text}
            """
       
        if reply_type == "super_datailed":
            max_attempt = 1
        elif reply_type == "detailed":
            max_attempt = 3
        else:
            max_attempt = 3

        for attempt in range(max_attempt):
            try:

                if user_id in VIP_USERS and reply_type == "super-detailed":
                    current_model = model_rotator.get_vip_model()
                elif user_id in PREMIUM_USERS and reply_type == "detailed":
                    current_model = model_rotator.get_premium_model() 
                else:
                    current_model = model_rotator.get_standard_model()

                if user_id not in VIP_USERS and reply_type == "super-detailed":
                    model_info = "Функция доступна только VIP пользователям. Свяжитесь с администраторам группы, чтобы получить VIP статус"
                elif user_id not in PREMIUM_USERS and reply_type == "detailed":
                    model_info = "Функция доступна только PREMIUM пользователям. Свяжитесь с администраторам группы, чтобы получить PREMIUM статус"
                else:
                    model_info = ""

                print(current_model)

                output = client.models.generate_content(
                    model=f"{current_model}",
                    contents=[
                        rules,
                        prompt
                    ],
                    config=config,
                )

                if model_info:
                    return f" \
                    <p>{model_info}</p>\
                    {output.text}\
                    "
                else:
                    return output.text
                
            except Exception as e:
                error_msg = str(e)

                if attempt < max_attempt - 1:
                    self.switch_model(current_model)
                    time.sleep(2)
                    continue

                else:
                    if "429" in error_msg:
                        print("Rate limit (429)")
                        return "Слишком много запросов. Подождите немного."
                    
                    elif "500" in error_msg or "503" in error_msg:
                        print("Серверная ошибка (5xx)")
                        return "Временные проблемы с сервером. Попробуйте позже. (Возможно перегружен)"
                        
                    elif "401" in error_msg or "403" in error_msg:
                        print("Ошибка аутентификации (401/403)")
                        return "Проблема с аутентификацией API"
                        
                    else:
                        print(f"Неизвестная ошибка: {error_msg}")
                        return "Временная ошибка сервиса"
            
model_rotator = ModelRotator()