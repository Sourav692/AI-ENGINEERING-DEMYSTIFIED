from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from rag_service import process_documents, ask_question

app = FastAPI()

@app.post("/upload")
async def upload_docs(files: list[UploadFile] = File(...)):
    try:
        file_paths = await process_documents(files)
        return {"message": "Documents processed and stored in vector DB", "files": file_paths}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/ask")
async def ask(prompt: str = Form(...)):
    try:
        answer, sources, retrieved_docs = ask_question(prompt)
        return {"answer": answer, "sources": sources, "retrieved_docs": retrieved_docs}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})