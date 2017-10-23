import json
import os
import re
from io import StringIO
from typing import List

import requests
from PIL import Image
from flask import Flask, jsonify
from flask import send_file
from gridfs import GridFS
from pymongo import MongoClient
from scipy.misc import imresize, imread, imsave

client = MongoClient('localhost', 27017)
grid = GridFS(client['test'])


class ImageHandler(object):
    """This class represents the Flask WebServer.
    """
    ORIGINAL_URL = 'http://54.152.221.29/images.json'

    def __init__(self, grid: GridFS):
        self.grid = grid
        self.download_originals()
        self.resize_images()
        self.persist_images()

    def download_originals(self) -> int:
        """
        Download the original images from ORIGINAL_URL.

        Return: the total of downloaded images.
        """
        r = requests.get(self.ORIGINAL_URL)
        images = json.loads(r.text)["images"]

        for image in images:
            url = image['url']
            r = requests.get(url, stream=True)
            filename = re.findall(r'.*/(.+)$', r.url)[0]
            with open('{}'.format(filename), 'wb') as f:
                for chunk in r:
                    f.write(chunk)

        return len(images)

    def list_images(self) -> List[str]:
        """
        List the images of the current directory.

        Return: a list with the JPG files of the current directory.
        """
        return [f for f in os.listdir() if f.endswith('.jpg') or f.endswith('.jpeg')]

    def resize_images(self) -> int:
        """
        Resizes the images of the {local directory},
        removing the original ones.

        Return: the total of resized images.
        """
        images = self.list_images()

        for filename in images:
            image = imread(filename)
            imsave('{name}_small.jpg'.format(name=filename.split('.')[0]), imresize(image, (240, 320)))
            imsave('{name}_medium.jpg'.format(name=filename.split('.')[0]), imresize(image, (288, 384)))
            imsave('{name}_large.jpg'.format(name=filename.split('.')[0]), imresize(image, (480, 640)))
            os.remove(filename)

        return len(images)

    def persist_images(self) -> None:
        """
        Resizes the images of the {local directory},
        removing the original ones.

        Return: the total of resized images.
        """
        for image in self.list_images():
            with open(image, 'rb') as f:
                self.grid.put(f, contentType='image/jpeg', filename=image)


app = Flask(__name__)
app.debug = True


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
    server = ImageHandler(grid)
    app.run()
