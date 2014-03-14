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

    def test_refresh_firewall(self):
        sfmc = SomaFMClient()
        sfmc.refresh('mp3', 'firewall')

        self.assertIsNotNone(sfmc.channels)
        self.assertNotEqual(len(sfmc.channels), 0)

    def test_refresh_no_channels(self):
        sfmc = SomaFMClient()
        sfmc.CHANNELS_URI = ''
        sfmc.refresh('mp3', 'fast')

        self.assertDictEqual(sfmc.channels, {})
        self.assertEqual(len(sfmc.channels), 0)

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

    def test_extractStreamUrlFromPls(self):
        url = "http://somafm.com/groovesalad.pls"
        sfmc = SomaFMClient()
        data = sfmc.extractStreamUrlFromPls(url)
        self.assertNotEqual(len(data), 0)
        self.assertNotEqual(data, url)

    def test_extractStreamUrlFromPls_unknown(self):
        url = "http://somafm.com/noneazerty.pls"
        sfmc = SomaFMClient()
        data = sfmc.extractStreamUrlFromPls(url)
        self.assertNotEqual(len(data), 0)
        self.assertEqual(data, url)
