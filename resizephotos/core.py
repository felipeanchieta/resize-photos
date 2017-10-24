import json
import re
from io import BytesIO
from typing import List, Any, Tuple, Generator

import requests
import rfc6266
from PIL import Image
from flask import Flask, jsonify, send_file
from gridfs import GridFS
from pymongo import MongoClient

IMGS_URL = 'http://54.152.221.29/images.json'
IMGS_SIZE = {'small': (320, 240), 'medium': (384, 288), 'large': (640, 480)}
MONGO_HOST = 'localhost'
MONGO_PORT = 27017
MONGO_DB = 'test'

MultipleSizesImage = Tuple[type(Image), type(Image), type(Image)]

_client = MongoClient(MONGO_HOST, MONGO_PORT)
_db = _client[MONGO_DB]
_client.drop_database(_db)
grid = GridFS(_client[MONGO_DB])

app = Flask(__name__)


def download_originals() -> Generator:
    """
    Download the original images from IMGS_URL

    Return: the total of downloaded images.
    """
    r = requests.get(IMGS_URL)
    j = json.loads(r.text)

    for img in j['images']:
        r = requests.get(img['url'])
        stream = BytesIO(r.content)
        img = Image.open(stream)
        img.filename = rfc6266.parse_requests_response(r).filename_unsafe
        yield img


def resize_image(img: type(Image)) -> Tuple[Any, Any, Any]:
    """Resize an image to small, medium and large.

    Return: a tuple containing a small, medium, large image considering the original input."""
    s_image = img.resize(IMGS_SIZE['small'])  # type: type(Image)
    s_image.filename = 'small_' + img.filename
    m_image = img.resize(IMGS_SIZE['medium'])  # type: type(Image)
    m_image.filename = 'medium_' + img.filename
    l_image = img.resize(IMGS_SIZE['large'])  # type: type(Image)
    l_image.filename = 'large_' + img.filename

    return s_image, m_image, l_image


def persist_image(img: type(Image)) -> bool:
    """Persist the JPG images of given path."""
    img_io = BytesIO()
    img.save(img_io, 'JPEG')
    img_io.seek(0)
    grid.put(img_io, contentType='image/jpeg', filename=img.filename)
    return True


@app.route('/')
def list_images_json():
    json_map = {}
    for image in grid.list():
        if re.match(r'^small_.*', image):
            json_map[image] = {'size': 'small', 'url': '/images/{}'.format(image)}
        elif re.match(r'^medium_.*', image):
            json_map[image] = {'size': 'medium', 'url': '/images/{}'.format(image)}
        elif re.match(r'^large_.*', image):
            json_map[image] = {'size': 'large', 'url': '/images/{}'.format(image)}
        else:
            json_map[image] = {'size': 'unknown', 'url': '/images/{}'.format(image)}

    return jsonify(json_map)


@app.route('/images/<path:filename>')
def get_image(filename: str) -> str:
    if not grid.exists(filename=filename):
        return '<h1>Not Found</h1>', 404
    else:
        img = Image.open(grid.get_last_version(filename=filename))
        img_io = BytesIO()
        img.save(img_io, 'JPEG')
        img_io.seek(0)
        return send_file(img_io, mimetype='image/jpeg')


@app.before_first_request
def initialize() -> None:
    imgs = list(download_originals())  # type: List[type(Image)]
    resized_imgs = [resize_image(img) for img in imgs]  # type: List[MultipleSizesImage]
    for small, medium, large in resized_imgs:
        persist_image(small)
        persist_image(medium)
        persist_image(large)


@app.errorhandler(404)
def page_not_found(_: Any) -> Tuple[str, int]:
    return '<h1>Not Found</h1>', 404


if __name__ == '__main__':
    app.run()
