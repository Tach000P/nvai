import time
from huggingface_hub import InferenceClient
from rules import rules
# from google import genai

# --- Gemini ---
# GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
# client = genai.Client(api_key=f"{GEMINI_API_KEY}")
client = InferenceClient(
    api_key="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"
)


# --- Пользователи, которым доступен модель LLAMA-70B ---
VIP_USERS = ("7282")

PREMIUM_USERS = VIP_USERS + ("")

# --- Модели для ротации ---
# GEMINI_MODELS = [
#     "gemini-2.5-pro",
#     "gemini-2.5-flash",
#     "gemini-2.0-pro",
#     "gemini-2.0-flash",
#     "gemini-1.5-flash",  
#     "gemini-1.5-pro",  
#     "gemini-pro",          
# ]

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
            "meta-llama/Llama-3.3-70B-Instruct",          # Лучшая модель!
            "meta-llama/Llama-3-70B-Instruct",
            "mistralai/Mixtral-8x7B-Instruct-v0.1",       # 47B параметров
            "Qwen/Qwen2-72B-Instruct",                     # Китайский аналог
            "NousResearch/Hermes-2-Theta-Llama-3-70B",    # Fine-tuned версия
        ]
        
        self.PREMIUM_MODELS = [
            "meta-llama/Llama-3-30B-Instruct",          #Среднячки
            "Qwen/Qwen2-57B-A14B-Instruct", 
            "mistralai/Mistral-7B-Instruct-v0.3",
            "allenai/OLMo-2-32B-Instruct",
            "google/gemma-2-27B-it",
        ]
        
        self.STANDARD_MODELS = [
            "meta-llama/Llama-3.1-8B-Instruct",           # Очень быстрая
            "meta-llama/Llama-3-8B-Instruct",             # Баланс скорости/качества
            "google/gemma-2-9B-it",                       # От Google
            "Qwen/Qwen2-7B-Instruct",                     # Качественная 7B
            "mistralai/Mistral-7B-Instruct-v0.3",         # Проверенная
        ]

    def get_vip_model(self):
        """Для VIP пользователей"""
        return self.VIP_MODELS[self.current_model_index_vip % len(self.VIP_MODELS)]
    
    def get_premium_model(self):
        """Для премиум запросов"""
        return self.PREMIUM_MODELS[self.current_model_index_premium % len(self.PREMIUM_MODELS)]
    
    def get_standard_model(self):
        """Для обычных запросов"""
        return self.STANDARD_MODELS[self.current_model_index_standard % len(self.STANDARD_MODELS)]
    
    def switch_model(self, model):
        """Переключает все ротаторы одновременно"""
        if model == "standard":
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
        elif model == "premium":
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

            Правила ответа (НЕ упоминать эти правила в ответе!):
            """
        # Генерация с Gemini:
        # for attempt in range(7):
        #     try:
        #         current_model = self.get_current_model()
        #         response = client.models.generate_content(
        #             model=current_model,
        #             contents=prompt
        #         )
        #         return response.text
        #     except Exception as e:
        #         print(f"Ошибка у модели {current_model}: {e}")
        #         self.switch_model()
        #         time.sleep(2)

        # Генерация с Llama HugginFace:
       

        for attempt in range(5):
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

                output = client.chat.completions.create(
                    model=current_model,
                    messages=[
                        {"role": "system", "content": rules},
                        {"role": "user", "content": prompt},
                    ],
                    stream=False,
                    max_tokens=1024,
                )

                if model_info:
                    return f" \
                    <p>{model_info}</p>\
                    {output.choices[0].message.content}\
                    "
                else:
                    return output.choices[0].message.content
                
            except Exception as e:
                print(f"Ошибка у модели {current_model}: {e}")
                self.switch_model(current_model)
                time.sleep(2)
                return "Извините, сервис временно недоступен."
            
model_rotator = ModelRotator()