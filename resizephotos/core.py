import json
import os
import re
from io import StringIO
from typing import List

import requests
from PIL import Image
from flask import Flask, jsonify, send_file
from gridfs import GridFS
from pymongo import MongoClient
from scipy.misc import imresize, imread, imsave

IMGS_URL = 'http://54.152.221.29/images.json'
MONGO_HOST = 'localhost'
MONGO_PORT = 27017
MONGO_DB = 'test'

client = MongoClient(MONGO_HOST, MONGO_PORT)
grid = GridFS(client[MONGO_DB])

app = Flask(__name__)
app.debug = True


def download_originals(path: str = '.') -> List[str]:
    """
    Download the original images from IMGS_URL

    Return: the total of downloaded images.
    """
    r = requests.get(IMGS_URL)
    images = json.loads(r.text)["images"]
    files = []

    for image in images:
        url = image['url']
        r = requests.get(url, stream=True)
        filename = re.findall(r'.*/(.+)$', r.url)[0]
        with open('{}'.format(path + '/' + filename), 'wb') as f:
            for chunk in r:
                f.write(chunk)
        files.append(filename)

    return files


def list_images(path: str = '.') -> List[str]:
    """
    List the JPG images of a given directory. Default: pwd.

    Return: list with the JPG filenames of given directory.
    """
    return [f for f in os.listdir(path) if f.endswith('.jpg') or f.endswith('.jpeg')]


def resize_images(images: List[str]) -> int:
    """
    Resize the images of given directory, removing the original ones after that.

    Return: the total number of resized images.
    """

    for filename in images:
        image = imread(filename)
        imsave('{name}_small.jpg'.format(name=filename.split('.')[0]), imresize(image, (240, 320)))
        imsave('{name}_medium.jpg'.format(name=filename.split('.')[0]), imresize(image, (288, 384)))
        imsave('{name}_large.jpg'.format(name=filename.split('.')[0]), imresize(image, (480, 640)))
        os.remove(filename)

    return len(images)


def persist_images(path: str = '.') -> None:
    """Persist the JPG images of given path."""
    for image in list_images(path):
        with open(path + '/' + image, 'rb') as f:
            grid.put(f, contentType='image/jpeg', filename=image)


@app.route('/')
def list_images_json():
    json_map = {}
    for image in grid.list():
        if re.match(r'.+small_\.jpe?g$', image):
            json_map[image] = {"size": "small", "url": "/images/{}".format(image)}
        elif re.match(r'.+medium\.jpe?g$', image):
            json_map[image] = {"size": "medium", "url": "/images/{}".format(image)}
        elif re.match(r'.+large\.jpe?g$', image):
            json_map[image] = {"size": "large", "url": "/images/{}".format(image)}
        else:
            json_map[image] = {"size": "unknown", "url": "/images/{}".format(image)}

    return jsonify(json_map)


@app.route('/images/<filename>')
def get_image(filename):
    if not grid.exists(filename=filename):
        raise Exception("This image is not here, try somewhere else!")
    else:
        stream = grid.get_last_version(filename)
        image = Image.open(stream)
        io = StringIO()
        image.save(io, 'JPEG', quality=100)
        io.seek(0)
        return send_file(stream, mimetype='image/jpeg')


if __name__ == '__main__':
    images = download_originals()
    resize_images(list_images())
    app.run()
