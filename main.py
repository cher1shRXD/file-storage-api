from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from PIL import Image
import os
import uuid
import shutil
from io import BytesIO

app = FastAPI()

UPLOAD_DIR = os.path.abspath("./uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/files/upload")
async def upload_file(file: UploadFile = File(...)):
    file_ext = os.path.splitext(file.filename)[1].lower()
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
    
    new_filename = f"{uuid.uuid4()}"
    
    if file_ext in image_extensions:
        file_content = await file.read()
        image = Image.open(BytesIO(file_content))
        
        if image.mode == 'P':
            image = image.convert('RGBA')
        
        new_filename = f"{new_filename}.webp"
        file_path = os.path.join(UPLOAD_DIR, new_filename)
        image.save(file_path, 'WEBP', quality=85)
    else:
        new_filename = f"{new_filename}{file_ext}"
        file_path = os.path.join(UPLOAD_DIR, new_filename)
        file.file.seek(0)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

    return {
        "filename": file.filename,
        "url": f"https://cloud.cher1shrxd.me/uploads/{new_filename}"
    }


@app.delete("/files/{filename}")
async def delete_file(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)

    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    os.remove(file_path)
    return JSONResponse(content={"message": "File deleted"}, status_code=200)


@app.get("/files")
async def list_files():
    """Get list of all files in the uploads directory"""
    try:
        files = []
        for filename in os.listdir(UPLOAD_DIR):
            file_path = os.path.join(UPLOAD_DIR, filename)
            if os.path.isfile(file_path):
                file_stat = os.stat(file_path)
                files.append({
                    "filename": filename,
                    "url": f"https://cloud.cher1shrxd.me/uploads/{filename}",
                    "size": file_stat.st_size,
                    "created_at": file_stat.st_ctime
                })
        
        files.sort(key=lambda x: x["created_at"], reverse=True)
        
        return {"files": files, "count": len(files)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
