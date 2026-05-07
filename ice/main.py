from ai import (
    create_collection,
    upload_data,
    process_query
)



create_collection()

upload_data()



# TEST QUERY


query = "форма не отправляется"

result = process_query(query)

print("\nRESULT:\n")

print(result)