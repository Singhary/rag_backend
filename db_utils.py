from prisma import Prisma
from prisma.models import Application_logs

db = Prisma()


async def insert_application_logs(session_id, user_query, gpt_response, model):
    await db.connect()
    await db.application_logs.create(
        {
            "session_id": session_id,
            "user_query": user_query,
            "gpt_response": gpt_response,
            "model": model,
        }
    )
    await db.disconnect()


async def get_chat_history(session_id):
    await db.connect()

    messages_data = await db.application_logs.find_many(
        where={"session_id": session_id},
        order={"created_at": "asc"},
    )

    messages = []
    for message in messages_data:
        messages.extend(
            [
                {"role": "human", "content": message.user_query},
                {"role": "ai", "content": message.gpt_response},
            ]
        )
    print(messages)
    await db.disconnect()
    return messages


async def insert_document_record(filename):
    await db.connect()

    file = await db.document_store.create(
        {
            "filename": filename,
        }
    )

    file_id = file.id

    await db.disconnect()

    return file_id

async def delete_document_record(file_id: int):
    await db.connect()
    try:
        # Check if the record exists
        record = await db.document_store.find_first(where={"id": file_id})
        if not record:
            print(f"No record found with id {file_id}")
            return False

        # Delete the record
        result = await db.document_store.delete(where={"id": file_id})
        if result:
            print(f"Record with id {file_id} deleted successfully.")
        else:
            print(f"Failed to delete record with id {file_id}")
            return False

        return True
    except Exception as e:
        print(f"Error while deleting record: {e}")
        return False
    finally:
        await db.disconnect()


async def get_all_documents():
    await db.connect()
    print("Connected to database")
    allFiles = await db.document_store.find_many()
    print(allFiles)
    await db.disconnect()
    
    return [dict(file) for file in allFiles]


