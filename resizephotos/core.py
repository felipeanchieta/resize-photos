import json
import re
from io import BytesIO, StringIO
from typing import List, Any, Tuple, Generator

import requests
import rfc6266 as rfc6266
from PIL import Image
from flask import Flask, jsonify, send_file
from gridfs import GridFS
from pymongo import MongoClient

IMGS_URL = 'http://54.152.221.29/images.json'
IMGS_SIZE = {"small": (240, 320), "medium": (288, 384), "large": (480, 640)}
MONGO_HOST = 'localhost'
MONGO_PORT = 27017
MONGO_DB = 'test'

MultipleSizesImage = Tuple[type(Image), type(Image), type(Image)]

_client = MongoClient(MONGO_HOST, MONGO_PORT)
_db = _client[MONGO_DB]
_client.drop_database(_db)
grid = GridFS(_client[MONGO_DB])

app = Flask(__name__)
app.debug = True


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
    s_image = img.resize(IMGS_SIZE["small"])  # type: type(Image)
    s_image.filename = "small_" + img.filename
    m_image = img.resize(IMGS_SIZE["medium"])  # type: type(Image)
    m_image.filename = "medium_" + img.filename
    l_image = img.resize(IMGS_SIZE["large"])  # type: type(Image)
    l_image.filename = "large_" + img.filename

    return s_image, m_image, l_image


def persist_image(img: type(Image), size: str = 'medium') -> bool:
    """Persist the JPG images of given path."""
    grid.put(img.tobytes(), contentType='image/jpeg', filename=img.filename)
    return True


@app.route('/')
def list_images_json():
    json_map = {}
    for image in grid.list():
        if re.match(r'^small_.*', image):
            json_map[image] = {"size": "small", "url": "/images/{}".format(image)}
        elif re.match(r'^medium_.*', image):
            json_map[image] = {"size": "medium", "url": "/images/{}".format(image)}
        elif re.match(r'^large_.*', image):
            json_map[image] = {"size": "large", "url": "/images/{}".format(image)}
        else:
            json_map[image] = {"size": "unknown", "url": "/images/{}".format(image)}

    return jsonify(json_map)


@app.route('/images/<filename>')
def get_image(filename):
    if not grid.exists(filename=filename):
        return "<h1>Not Found</h1>", 404
    else:
        stream = grid.get_last_version(filename)
        image = Image.open(stream)
        io = StringIO()
        image.save(io, 'JPEG', quality=100)
        io.seek(0)
        return send_file(stream, mimetype='image/jpeg')


@app.before_first_request
def initialize() -> None:
    imgs = list(download_originals())  # type: List[type(Image)]
    resized_imgs = [resize_image(img) for img in imgs]  # type: List[MultipleSizesImage]
    for small, medium, large in resized_imgs:
        persist_image(small, size='small')
        persist_image(medium, size='medium')
        persist_image(large, size='large')


@app.errorhandler(404)
def page_not_found(_: Any) -> Tuple[str, int]:
    return "<h1>Not Found</h1>", 404


if __name__ == '__main__':
    app.run()
