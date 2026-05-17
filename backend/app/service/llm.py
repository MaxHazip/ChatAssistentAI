import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

def generate_llm_answer(user_query: str, context_text: str):
    
    system_instruction = """
    Ты — интеллектуальный шлюз безопасности и модератор клиентской поддержки.
    Перед тобой стоит задача: сопоставить ВОПРОС пользователя и КОНТЕКСТ из базы знаний.
    
    Применяй жесткие правила модерации:
    1. Если ВОПРОС содержит оскорбления, нецензурную брань, агрессию, провокации или является абсолютной бессмыслицей (набором букв) — ты обязан ответить ТОЛЬКО одним словом: [NONSENSE]
    2. Если ВОПРОС сформулирован нормально, но КОНТЕКСТ вообще не содержит ответа на него (темы абсолютно разные, например: вопрос про личные оскорбления, а контекст про настройки DNS или домены) — ты обязан ответить ТОЛЬКО одним словом: [NOT_FOUND]
    3. Если ВОПРОС адекватен и КОНТЕКСТ действительно содержит ответ — аккуратно выдели главное из контекста и напиши один краткий, вежливый ответ для клиента.
    
    Строго запрещено: отвечать на оскорбления взаимностью, вступать в дискуссию, если вопрос признан некорректным, или использовать внешние знания вне контекста.
    """

    user_content = f"КОНТЕКСТ ИЗ БАЗЫ ЗНАНИЙ:\n{context_text}\n\nВОПРОС ПОЛЬЗОВАТЕЛЯ:\n{user_query}"

    try:
        response = client.chat.completions.create(
            model="baidu/cobuddy:free",
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_content}
            ],
            temperature=0.0, 
            extra_body={"reasoning": {"enabled": True}}
        )
        
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        print(f"Ошибка вызова CoBuddy: {e}")
        return "[ERROR]"