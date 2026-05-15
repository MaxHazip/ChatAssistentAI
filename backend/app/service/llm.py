import os
from dotenv import load_dotenv
from openai import OpenAI

# Загружаем ключ из .env
load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

def generate_llm_answer(user_query: str, context_text: str):
    """
    Вызов Baidu CoBuddy с включенным reasoning для фильтрации и суммаризации.
    """
    system_instruction = """
    Ты — интеллектуальный модератор поддержки. 
    1. Проанализируй вопрос пользователя. Если это случайный набор букв, бессмыслица или спам — ответь только одним словом: [NONSENSE]
    2. Если вопрос понятен, посмотри на предоставленный КОНТЕКСТ.
    3. Если в КОНТЕКСТЕ нет ответа — ответь только одним словом: [NOT_FOUND]
    4. Если ответ есть — сформируй единый вежливый ответ на основе контекста.
    """

    user_content = f"КОНТЕКСТ:\n{context_text}\n\nВОПРОС:\n{user_query}"

    try:
        response = client.chat.completions.create(
            model="baidu/cobuddy:free",
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_content}
            ],
            # Включаем логику рассуждений, как в твоем примере
            extra_body={"reasoning": {"enabled": True}}
        )
        
        # Модели с reasoning могут возвращать основной контент здесь
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        print(f"Ошибка вызова CoBuddy: {e}")
        return "[ERROR]"