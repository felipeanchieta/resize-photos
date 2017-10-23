#import unittest
#from unittest import mock
#
#from PIL.Image import Image
#
#from resizephotos import core
#
#
#class TestResizePhotos(unittest.TestCase):
#    pass
#
#
#class TestDownloadOriginals(TestResizePhotos):
#    ret_json = '{"images": [{"url": "http://server.com/img1.jpg"}, {"url": "http://server.com/img2.jpg"}]}'
#
#    @mock.patch('__main__.open', mock.mock_open())
#    @mock.patch('requests.get', side_effect=[mock.MagicMock(text=ret_json),
#                                             mock.MagicMock(url="http://server.com/img1.jpg"),
#                                             mock.MagicMock(url="http://server.com/img2.jpg")])
#    def test_download_originals(self, mock_get):
#        self.assertEqual(['img1.jpg', 'img2.jpg'], core.download_originals())
#        mock_get.assert_has_calls([mock.call("http://54.152.221.29/images.json"),
#                                   mock.call("http://server.com/img1.jpg", stream=True),
#                                   mock.call("http://server.com/img2.jpg", stream=True)])
#
#
#class TestListImages(TestResizePhotos):
#    @mock.patch('os.listdir', side_effect=[['a.txt', 'b.mp3', 'c.jpg', 'd.jpeg', 'e.png'],
#                                           ['f.zip', 'g.gzip', 'h.jpg']])
#    def test_list_images(self, mock_listdir):
#        self.assertEqual(['c.jpg', 'd.jpeg'], core.list_images())
#        mock_listdir.assert_called_with('.')
#        self.assertEqual(['h.jpg'], core.list_images('dir/'))
#        mock_listdir.assert_called_with('dir/')
#
#
#class TestResizeImages(TestResizePhotos):
#    def setUp(self):
#        self.images = ['img1.jpg', 'img2.jpg', 'img3.jpg']
#
#    @mock.patch('os.remove')
#    @mock.patch('resizephotos.core.imsave')
#    @mock.patch('resizephotos.core.imresize')
#    @mock.patch('resizephotos.core.imread', side_effect=[Image(), Image(), Image()])
#    def test_resize_images(self, mock_imread, mock_imresize, mock_imsave, mock_remove):
#        """Test resize_images function"""
#        self.assertEqual(3, core.resize_images(self.images))
#
#        mock_imread.assert_has_calls([mock.call('img1.jpg'), mock.call('img2.jpg'), mock.call('img3.jpg')])
#        mock_imresize.assert_has_calls(
#            [mock.call(mock.ANY, (240, 320)), mock.call(mock.ANY, (288, 384)), mock.call(mock.ANY, (480, 640)),
#             mock.call(mock.ANY, (240, 320)), mock.call(mock.ANY, (288, 384)), mock.call(mock.ANY, (480, 640)),
#             mock.call(mock.ANY, (240, 320)), mock.call(mock.ANY, (288, 384)), mock.call(mock.ANY, (480, 640))])
#        mock_imsave.assert_has_calls([mock.call('img1_small.jpg', mock.ANY), mock.call('img1_medium.jpg', mock.ANY),
#                                      mock.call('img1_large.jpg', mock.ANY), mock.call('img2_small.jpg', mock.ANY),
#                                      mock.call('img2_medium.jpg', mock.ANY), mock.call('img2_large.jpg', mock.ANY),
#                                      mock.call('img3_small.jpg', mock.ANY), mock.call('img3_medium.jpg', mock.ANY),
#                                      mock.call('img3_large.jpg', mock.ANY)])
#        mock_remove.assert_has_calls([mock.call('img1.jpg'), mock.call('img2.jpg'), mock.call('img3.jpg')])
#
#
## class TestPersistImages(TestResizePhotos):
##    @mock.patch('__main__.open', mock.mock_open(read_data=Image()))
##    @mock.patch('os.listdir', return_value=['c.jpg', 'd.jpeg', 'e.png'])
##    @mock.patch('resizephotos.core.GridFS')
##    def test_persist_images(self, mock_listdir, mock_grid):
##        core.persist_images()
#
#
#if __name__ == '__main__':
#    unittest.main()
