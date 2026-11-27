import os
from dotenv import load_dotenv
from groq import Groq
from services.interfaces import IAIService

load_dotenv()


class GroqAIService(IAIService):
    def __init__(self, api_key: str | None = None, model: str = "openai/gpt-oss-120b"):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.model = model

        if not self.api_key or "встав_сюди" in self.api_key:
            raise ValueError("Ключ GROQ_API_KEY не знайдено у файлі .env")

        self.client = Groq(api_key=self.api_key)

    def generate_content(
        self,
        topic: str,
        tone: str,
        content_type: str,
        option_label: str,
    ) -> str:
        if content_type == "tips":
            if "18" in option_label:
                system_prompt = (
                    "Ти — топовий SMM-стратег та контент-продюсер. "
                    "Пиши бездоганною літературною українською мовою без русизмів та суржику. "
                    "Склади рівно 18 практичних порад на задану тему. "
                    "Для КОЖНОЇ поради обов'язково розпиши конкретні покрокові дії, як її впровадити на практиці. "
                    "Оформлюй чітким нумерованим списком."
                )
            else:
                count = "14" if "14" in option_label else "8"
                system_prompt = (
                    "Ти — професійний SMM-експерт для Instagram та TikTok. "
                    "Пиши бездоганною літературною українською мовою без русизмів та суржику. "
                    f"Склади рівно {count} чітких, корисних і практичних порад на задану тему. "
                    "Оформлюй нумерованим списком із коротким поясненням кожного пункту."
                )
            user_prompt = f"Тема для порад: «{topic}». Формат: {option_label}."
            max_tokens = 2048 if "18" in option_label else 1400
        else:
            system_prompt = (
                "Ти — професійний україномовний SMM-сценарист для TikTok та Instagram Reels. "
                "Пиши бездоганною літературною українською мовою за чинним правописом, без суржику та русизмів. "
                f"Розрахуй темп, обсяг тексту та таймінг сценарію рівно на тривалість: {option_label}.\n\n"
                "Обов'язкова структура відповіді:\n"
                "🎯 **Хук (перші 3 секунди):** фраза або дія, яка миттєво чіпляє увагу.\n"
                f"🎬 **Основна частина ({option_label}):** таймінг по секундах, текст озвучки та опис кадру.\n"
                "📣 **Заклик до дії (CTA):** фінал для коментарів, збережень або підписки.\n"
                "#️⃣ **Хештеги:** 5 релевантних хештегів українською мовою."
            )
            user_prompt = (
                f"Напиши сценарій відео на тему: «{topic}». "
                f"Тривалість ролика: {option_label}. Тон подачі: {tone}."
            )
            max_tokens = 1200

        chat_completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.45,
            max_tokens=max_tokens,
        )
        return chat_completion.choices[0].message.content