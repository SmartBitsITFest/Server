import cv2
import json
import ollama
import requests
import numpy as np
from pyzbar import pyzbar
from serpapi.google_search import GoogleSearch


upcdb_key = '937A8567AA2ACF7E3F079DB6A050F719'
url = "https://api.upcdatabase.org/search/?query={}&page=1"
prompt_template = 'I have {}. Give me {} about it.'
headers = {
  'Authorization': 'Bearer 937A8567AA2ACF7E3F079DB6A050F719',
  'Cookie': 'upcdatabaseorg=7vd4hb3ji1rb8vrbbabol82k85'
}
#TODO: Add rotation to the images

async def prompt_llama_model(product_name, prompt):
    # Create an instance of the OpenAI GPT-3 model
    model = ollama.AsyncClient()

    # Generate a response to the prompt
    response = model.generate('notux', prompt_template.format(product_name, prompt))

    # Return the response
    return await response

def get_product_name_if_first_try_failed(barcode_data):
    query = f'site:www.istoric-preturi.info {barcode_data}'
    api_url = "https://api.duckduckgo.com"

    params = {
        "engine": "google",
        "q": query,
        "api_key": "1955d9c26c30b21d333f10c17982152740dc44418401dce38c174aeafec11c67"
    }

    search = GoogleSearch(params)
    results = search.get_dict()
    shopping_results = results["organic_results"]

    product_name = shopping_results[0]['title'].split('-')[0]
    return product_name


async def read_barcode(image_bytes):
    # Create a numpy array from the image bytes
    nparr = np.frombuffer(image_bytes, np.uint8)
    image_array = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
    images = [
        image_array,
        cv2.rotate(image_array, cv2.ROTATE_90_CLOCKWISE),
        cv2.rotate(image_array, cv2.ROTATE_90_COUNTERCLOCKWISE),
        cv2.rotate(image_array, cv2.ROTATE_180),
    ]

    # Find barcodes in the image
    barcodes = list(map(pyzbar.decode, images))
    barcodes = [barcode for sublist in barcodes for barcode in sublist]
    

    # Loop over detected barcodes
    for barcode in barcodes:
        # Extract the barcode data
        barcode_data = barcode.data.decode("utf-8")
        barcode_type = barcode.type

        # Print the barcode data and type
        print("Barcode Data:", barcode_data)
        print("Barcode Type:", barcode_type)

        # Make a request to the UPC Database API
        response = requests.get(url.format(barcode_data), headers=headers)
        print(response.text)
        data = json.loads(response.text)
        success = data['success']
        if success:
            # Return the barcode data
            return {'product_name': 
                    data['items'][0]['title']}
        else:
            product_name = get_product_name_if_first_try_failed(barcode_data)
            return {'product_name': product_name}

    
    return {
        "message": "No barcode found"
    }
