import easyocr
from fastapi import APIRouter, WebSocket
from PIL import Image
import io
import os
import sys
import json

from services import barcode
from services import exp_date
router = APIRouter()

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
        if extracted_bytes == b'BARC':  # Hex value of 'BARC'
            response = await barcode.read_barcode(data[4:])
            await websocket.send_text(json.dumps(response))
            await save_image(data[4:], "image.jpg")
        elif extracted_bytes == b'EXPD':  # Hex value of 'EXPD'
            expiration_date = await exp_date.full_exp_date_detection(data[4:])
            await websocket.send_text(json.dumps(expiration_date))
            await save_image(data[4:], "image.jpg")
        else:
            await websocket.send_text("Operation not supported")
