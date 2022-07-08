"""
Microsoft's documentation: https://docs.microsoft.com/en-us/bing/search-apis/bing-image-search/quickstarts/rest/python
"""

import configparser
from typing import Callable, Iterable

import requests
import matplotlib.pyplot as plt
from PIL import Image
from io import BytesIO
import os

credentials = configparser.ConfigParser()
credentials.read("credentials.ini")

config = configparser.ConfigParser()
config.read("config.ini")

SEARCH_URL = config['DEFAULT']['search_url']
SEARCH_TERMS = config['DEFAULT']['search_term'].split(',')
SUBSCRIPTION_KEY = credentials['DEFAULT']['subscription_key']

HEADERS = {"Ocp-Apim-Subscription-Key" : SUBSCRIPTION_KEY}

MAX_RESULTS = 100

DIR_BASE = "./data/"

def params_generator(search_term: str) -> Iterable:
    return {"q": search_term, "license": "modify", "imageType": "photo"}

def response_generator(param: Iterable) -> Iterable:
    return requests.get(SEARCH_URL, headers=HEADERS, params=param)

def img_link_generator(response: Iterable) -> Iterable:
    """
    """
    response.raise_for_status()
    result = response.json()
    for img in result["value"]:
        yield img["thumbnailUrl"]
    #return (img["thumbnailUrl"] for img in result["value"])

def download_image(link: str) -> Callable:
    image_data = requests.get(link)
    image_data.raise_for_status()
    return Image.open(BytesIO(image_data.content))

def create_directory(label: str) -> None:
    os.makedirs(f"{DIR_BASE}{label}/", exist_ok=True)
    print(f"Directory created for {label}.")

def save_image(image: Callable, label: str, id: int) -> None:
    plt.imshow(image)
    plt.axis('off')
    plt.savefig(f"{DIR_BASE}{label}/{id}.jpeg", bbox_inches='tight', pad_inches=0.0)
    plt.close()

def pipeline(links):
    print("Running...")

    for label in links.keys():
        create_directory(label=label)
        for idx, link in enumerate(links[label]):
            if idx <= MAX_RESULTS:
                image = download_image(link=link)
                save_image(image, label, idx)

    print(f"Images saved in the '{DIR_BASE}' directory.")

if __name__ == "__main__":

    links = {
        search_term: img_link_generator(response_generator(params_generator(search_term))) \
            for search_term in SEARCH_TERMS
    }
    
    pipeline(links=links)