from huggingface_hub import InferenceClient

client = InferenceClient(
    api_key="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"
)

# --- Пользователи, которым доступен генерация изображений ---
VIP_USERS = ("7282")

PREMIUM_USERS = VIP_USERS + ("")

def generate_image():
    # image = client.text_to_image("An astronaut riding a horse on the moon.")
    # image.save("astronaut.png")

    image = client.text_to_image(
        "Cat with boots",
        negative_prompt="low resolution, blurry",
        model="segmind/SSD-1B",
    )
    image.save("better_astronaut.png")

generate_image()