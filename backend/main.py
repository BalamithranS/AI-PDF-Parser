import os
import json
import shutil
from fastapi import FastAPI, Request, UploadFile, File
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse
from backend.parser import extract_pdf_content

app = FastAPI()
templates = Jinja2Templates(directory="backend/templates")

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.post("/upload")
async def upload_pdf(request: Request, pdf: UploadFile = File(...)):
    os.makedirs("backend/uploads", exist_ok=True)
    os.makedirs("output", exist_ok=True)
    
    file_path = os.path.join("backend", "uploads", pdf.filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(pdf.file, buffer)
    
    text = extract_pdf_content(file_path)
    
    data = {"filename": pdf.filename, "content": text}
    output_path = os.path.join("output", f"{pdf.filename}.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
        
    return templates.TemplateResponse(
        request=request, 
        name="index.html", 
        context={"result": text[:1000], "filename": pdf.filename}
    )

@app.get("/download/{filename}")
async def download_json(filename: str):
    file_path = os.path.join("output", f"{filename}.json")
    return FileResponse(path=file_path, media_type='application/json', filename=f"{filename}.json")