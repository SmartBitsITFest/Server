import asyncio
import json
import cv2
import numpy as np
from serpapi.google_search import GoogleSearch

from services import barcode

async def test():
    resp = await barcode.read_barcode(open("test.jpg", "rb").read())
    print(resp)

#asyncio.run(test())
data = '''
{
    "success": true,
    "timestamp": 1709937151,
    "results": 1,
    "items": [
        {
            "barcode": "5942289000119",
            "title": "Tedi-morcov banana mar",
            "alias": null,
            "description": ""
        }
    ]
}
'''

print(json.loads(data))


image = cv2.imread("image.jpg")

images = [
    image,
    cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE),
    cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE),
    cv2.rotate(image, cv2.ROTATE_180),
]
images = list(
    map(
        lambda img: cv2.resize(img, (300, 300)),
        images
    )

)

top = np.concatenate((images[0], images[1]), axis=1)
bottom = np.concatenate((images[2], images[3]), axis=1)
combined = np.concatenate((top, bottom), axis=0)

# Save the combined image
cv2.imwrite("combined_image.jpg", combined)

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

print(get_product_name_if_first_try_failed("5942289000119"))

