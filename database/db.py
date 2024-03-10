from pymongo import MongoClient
from typing import List
from models.product import Product, ProductUpdate

uri = "mongodb+srv://cluster0.qfqn9z0.mongodb.net/?authSource=%24external&authMechanism=MONGODB-X509&retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(uri,
                     tls=True,
                     tlsCertificateKeyFile='./cert.pem')

database = client['ITFestSB']
collection = database['Products']

def insert(product: Product):
    return collection.insert_one(product.dict())


def get_by_id(id: str) -> Product:
    return collection.find_one({"_id": id})


def get_by_name(name: str) -> List[Product]:
    return list(collection.find({"name": name}))

def get_all() -> List[Product]:
    return list(collection.find())


def delete(id: str):
    return collection.delete_one({"_id": id})


def delete_all():
    return collection.delete_many({})


def update(id: str, product: ProductUpdate):
    return collection.update_one({"_id": id}, {"$set": product.dict()})

