import easyocr
from fastapi import APIRouter, WebSocket
from PIL import Image
import io
import os
import sys
import json

from services import barcode

router = APIRouter()

eocr_reader = reader = easyocr.Reader(['en'], detect_network='dbnet18',
                                      model_storage_directory='../easy_ocr_models/')  # this needs to run only once to load the model into memory


async def save_image(image_data: bytes, file_path: str):
    image = Image.open(io.BytesIO(image_data))
    image.save(file_path)
    return {"message": "Image saved successfully!"}


@router.get("/ai/prompt")
async def prompt_llama_model(product_name: str, prompt: str):
    response = await barcode.prompt_llama_model(product_name, prompt)
    return {"response": response}


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_bytes()
        extracted_bytes = data[:4]
        if extracted_bytes == [0x42, 0x41, 0x52, 0x43]:  # Hex value of 'BARC'
            response = await barcode.read_barcode(data[4:])
            await websocket.send_text(json.dumps(response))
            await save_image(data[4:], "image.jpg")
        elif extracted_bytes == [0x45, 0x58, 0x50, 0x44]:  # Hex value of 'EXPD'
            pass
        else:
            await websocket.send_text("Operation not supported")
