from ai import (
    create_collection,
    upload_data,
    process_query
)

# создаем коллекцию
create_collection()

# загружаем данные
upload_data()

# тестовые запросы
test_queries = [
    "не работает форма",
    "форма не отправляется",
    "не могу войти",
    "сайт грузится долго",
    "как поменять телефон",
    "где посмотреть рекламу",
    "страницы сломались",
    "не открывается админка",
    "нужна помощь",
    "ничего не работает"
]

print("\n========== TESTING ==========\n")

for query in test_queries:

    result = process_query(query)

    print(f"QUERY: {query}")
    print(f"STATUS: {result['status']}")
    print(f"SCORE: {result['score']}")
    print(f"ANSWER: {result['answer']}")

    if "questions" in result:
        print("CLARIFICATION QUESTIONS:")

        for q in result["questions"]:
            print("-", q)

    print("\n----------------------\n")