import tempfile
import unittest

import os

from resizephotos import core


class FlaskrTestCase(unittest.TestCase):
    def setUp(self):
        self.db_fd, core.app.config['DATABASE'] = tempfile.mkstemp()
        core.app.testing = True
        self.app = core.app.test_client()
        with core.app.app_context():
            core.app.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(core.app.config['DATABASE'])


if __name__ == '__main__':
    unittest.main()
