from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import uuid
from processor import process_id_photo
from database import create_order, update_order_status, get_order

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class OrderCreate(BaseModel):
    size_preset: str
    bg_color: str

@app.post("/create-order")
async def create_pre_order(data: OrderCreate):
    order_id = str(uuid.uuid4())
    create_order(order_id, data.size_preset, data.bg_color)
    return {"order_id": order_id}

@app.post("/activate-order")
async def activate_order(order_id: str):
    # In production, verify PayPal payment here
    update_order_status(order_id, "COMPLETED")
    return {"status": "success"}

@app.post("/generate")
async def generate_photo(
    file: UploadFile = File(...),
    color: str = "#FFFFFF",
    size: str = "us_passport"
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    try:
        contents = await file.read()
        processed_image_bytes = process_id_photo(contents, bg_color_hex=color, preset_key=size)
        
        return StreamingResponse(
            processed_image_bytes, 
            media_type="image/jpeg",
            headers={"Content-Disposition": "attachment; filename=id_photo.jpg"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#if __name__ == "__main__":
#    import os
#    port = int(os.environ.get("PORT",8000))
#    printf("端口：{port}")
#    uvicorn.run("main:app", host="0.0.0.0", port = port,reload=False)
