import unittest

from mopidy_somafm.somafm import SomaFMClient


class SomaFMClientTest(unittest.TestCase):

    def test_init_proxy(self):
        proxy = "http://user:pass@proxy.lan:8080"
        sfmc = SomaFMClient(proxy=proxy)
        self.assertIn('http', sfmc.proxies)
        self.assertEqual(sfmc.proxies['http'], proxy)

    def test_refresh(self):
        sfmc = SomaFMClient()
        sfmc.refresh('mp3', 'fast')

        self.assertIsNotNone(sfmc.channels)
        self.assertNotEqual(len(sfmc.channels), 0)

    def test_downloadContent_ok(self):
        url = "http://api.somafm.com/channels.xml"
        sfmc = SomaFMClient()
        data = sfmc._downloadContent(url)
        self.assertNotEqual(len(data), 0)

    def test_downloadContent_ko(self):
        url = "http://api.somafm.com/channels.xml.ko"
        sfmc = SomaFMClient()
        data = sfmc._downloadContent(url)
        self.assertIsNone(data)
