import easyocr
from fastapi import APIRouter, UploadFile, WebSocket
from PIL import Image
import io
import os
import sys
import json
import speech_recognition as sr
from speech_recognition import google
from database import db

from services import barcode
from services import exp_date
from services import product
router = APIRouter()

async def save_image(image_data: bytes, file_path: str):
    image = Image.open(io.BytesIO(image_data))
    image.save(file_path)
    return {"message": "Image saved successfully!"}


@router.get('/products/', tags=['products'])
async def get_products():
    return db.get_all()


@router.get('/products/{product_id}', tags=['products'])
async def get_product(product_id: str):
    return db.get_by_id(product_id)


@router.get('/products/name/{product_name}', tags=['products'])
async def get_product_by_name(product_name: str):
    return db.get_by_name(product_name)


@router.post('/products/', tags=['products'])
async def create_product(product: db.Product):
    return db.insert(product)


@router.put('/products/{product_id}', tags=['products'])
async def update_product(product_id: str, product: db.ProductUpdate):
    return db.update(product_id, product)


@router.delete('/products/{product_id}', tags=['products'])
async def delete_product(product_id: str):
    return db.delete(product_id)


@router.delete('/products/', tags=['products'])
async def delete_all_products():
    return db.delete_all()


@router.post("/ai/{product_name}/prompt/", tags=['ai'])
async def prompt_llama_model(product_name: str, prompt: UploadFile):
    r = sr.Recognizer()
    audio_bytes = sr.AudioFile(prompt.file)
    audio_data = sr.AudioData(audio_bytes, 16000, 2)
    prompt_text = r.recognize_google(audio_data, language="en-US")
    print(prompt_text)
    response = await barcode.prompt_llama_model(product_name, prompt_text)
    return {"response": response}


@router.get('/ai/recipes', tags=['ai'])
async def get_recipes_from_ai():
    products = db.get_all()
    prompt_text = f'I have these products: {", ".join([product.name for product in products])}. What can I cook using either all or a subset of these items?'
    response = await product.prompt_llama_model(prompt_text)
    return {'recipes': response}

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
            expiration_date = exp_date.full_exp_date_detection(data[4:])
            await websocket.send_text(json.dumps('expiration date not functional yet'))
            await save_image(data[4:], "image.jpg")
        else:
            await websocket.send_text("Operation not supported")


@router.websocket("/ws/ai")
async def websocket_microphone_prompt(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_bytes()
        r = sr.Recognizer()
        text = r.recognize_google(data, language="en-US")
        print(text)

        
