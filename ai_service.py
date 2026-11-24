import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

def generate_smm_script(topic: str, tone: str) -> str:
    """Генерує SMM-сценарій для Reels/TikTok через Groq API."""
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key or "встав_сюди" in api_key:
        raise ValueError("Ключ GROQ_API_KEY не знайдено у файлі .env")

    client = Groq(api_key=api_key)

    chat_completion = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "system",
                "content": (
                    "Ти — професійний SMM-сценарист для TikTok та Instagram Reels. "
                    "Пиши живі, природні сценарії українською мовою без води. "
                    "Обов'язкова структура відповіді:\n"
                    "🎯 **Хук (перші 3 секунди):** фраза або дія, яка миттєво чіпляє увагу.\n"
                    "🎬 **Основна частина:** текст озвучки та короткі підказки, що відбувається в кадрі.\n"
                    "📣 **Заклик до дії (CTA):** фінал для коментарів, збережень або підписки.\n"
                    "#️⃣ **Хештеги:** 5 релевантних хештегів."
                ),
            },
            {
                "role": "user",
                "content": f"Напиши сценарій відео на тему: «{topic}». Тон подачі: {tone}.",
            },
        ],
        temperature=0.7,
        max_tokens=1024,
    )

    return chat_completion.choices[0].message.content