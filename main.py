__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
import logging
import os
import shutil
import uuid
from chroma_utils import delete_doc_from_chroma, index_document_to_chroma
from db_utils import (
    delete_document_record,
    get_all_documents,
    get_chat_history,
    insert_application_logs,
    insert_document_record,
)
from fastapi import FastAPI, File, HTTPException, UploadFile
from langchain_utils import get_rag_chain
from pydantic_models import DeleteFileRequest, DocumentInfo, QueryInput, QueryResponse

logging.basicConfig(filename="app.log", level=logging.INFO)

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Welcome to the AI Chatbot API!"}

@app.post("/chat", response_model=QueryResponse)
async def chat(query_input: QueryInput):
    session_id = query_input.session_id or str(uuid.uuid4())
    logging.info(
        f"Session ID: {session_id}, User Query: {query_input.question}, Model: {query_input.model.value}"
    )

    chat_history = await get_chat_history(session_id)
    rag_chain =  get_rag_chain(query_input.model.value)

    answer = rag_chain.invoke(
        {
            "input": query_input.question,
            "chat_history": chat_history,
        }
    )["answer"]

    await insert_application_logs(
        session_id, query_input.question, answer, query_input.model.value
    )
    logging.info(f"Session ID: {session_id}, AI Response: {answer}")
    return QueryResponse(answer=answer, session_id=session_id, model=query_input.model)


@app.post("/upload-doc")
async def upload_and_index_document(file: UploadFile = File(...)):
    allowed_extensions = [".pdf", ".docx", ".html"]
    print(f"file information_in_main_api: {file}")
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided.")
    file_extension = os.path.splitext(file.filename)[1].lower()

    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed types are: {', '.join(allowed_extensions)}",
        )

    temp_file_path = f"temp_{file.filename}"

    try:
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

            file_id = await insert_document_record(file.filename)
            success = index_document_to_chroma(temp_file_path, file_id)

        if success:
            return {
                "message": f"File {file.filename} has been successfully uploaded and indexed.",
                "file_id": file_id,
            }
        else:
            await delete_document_record(file_id)
            raise HTTPException(
                status_code=500, detail=f"Failed to index {file.filename}."
            )

    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)


@app.get("/list-docs", response_model=list[DocumentInfo])
async def list_document():
    return await get_all_documents()


@app.post("/delete-doc")
async def delete_document(request: DeleteFileRequest):
    chroma_delete_success =  delete_doc_from_chroma(request.file_id)
    print(request.file_id)

    if chroma_delete_success:
        db_delete_success = await delete_document_record(request.file_id)

        if db_delete_success:
            return {
                "message": f"Successfully deleted document with file_id {request.file_id} from the system."
            }

        else:
            return {
                "error": f"Deleted from Chroma but failed to delete document with file_id {request.file_id} from the database."
            }

    else:
        return {
            "error": f"Failed to delete document with file_id {request.file_id} from Chroma."
        }
        

