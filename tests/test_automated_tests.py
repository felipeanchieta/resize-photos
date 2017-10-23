import json
import unittest
from typing import Sequence, List, Any, Tuple

import requests
from PIL import Image

from resizephotos import core

MultipleSizesImage = Tuple[type(Image), type(Image), type(Image)]


class SanityCheckTest(unittest.TestCase):
    def setUp(self):
        self.sanity_check()

    def assertNotEmpty(self, obj: Sequence) -> None:
        """Asserts that a Sequence is not empty."""
        self.assertGreater(len(obj), 0)

    def sanity_check(self):
        """Asserts the ideal conditions for the remote image server."""
        r = requests.get('http://54.152.221.29/images.json')  # type: requests.Response
        self.assertEqual(r.status_code, 200)
        self.assertIn('content-type', r.headers)
        self.assertRegex(r.headers['content-type'], r'application/json')
        self.assertNotEmpty(r.text)

        j = json.loads(r.text)
        self.assertNotEmpty(j)
        self.assertIn("images", j)
        r.close()

        imgs = j["images"]  # type: List[Any]
        for img in imgs:
            self.assertNotEmpty(img)
            self.assertIn("url", img)
            self.assertNotEmpty(img["url"])
            r = requests.get(img["url"])  # type: requests.Response
            self.assertEqual(r.status_code, 200)
            self.assertIn('content-type', r.headers)
            self.assertRegex(r.headers['content-type'], r'image/jpeg')
            r.close()

    def test_whole_process(self):
        """Test the whole process of downloading the originals,
        resizing them and persisting in Mongo"""

        # Download images
        imgs = list(core.download_originals())  # type: List[type(Image)]
        self.assertGreater(len(imgs), 0)

        # Resize images
        resized_imgs = [core.resize_image(img) for img in imgs]  # type: List[MultipleSizesImage]
        for small, medium, large in resized_imgs:
            self.assertTupleEqual((240, 320), small.size)
            self.assertTupleEqual((288, 384), medium.size)
            self.assertTupleEqual((480, 640), large.size)

        # Persist images
        for small, medium, large in resized_imgs:
            self.assertTrue(core.persist_image(small, size='small'))
            # self.assertTrue(core.grid.exists(small.filename))
            self.assertTrue(core.persist_image(medium, size='medium'))
            # self.assertTrue(core.grid.exists(medium.filename))
            self.assertTrue(core.persist_image(large, size='large'))
            # self.assertTrue(core.grid.exists(large.filename))

        print(core.grid.list())


if __name__ == '__main__':
    unittest.main()
