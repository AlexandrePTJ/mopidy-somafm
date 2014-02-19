import unittest

from mopidy_somafm.actor import format_proxy, parse_uri


class ActorTest(unittest.TestCase):

    def test_format_proxy(self):
        self.assertEqual(format_proxy(
            '', '', '', '', 0
            ), None)
        self.assertEqual(format_proxy(
            '', '', '', 'proxy.lan', 0
            ), 'http://proxy.lan:80')
        self.assertEqual(format_proxy(
            'https', '', '', 'proxy.lan', 0
            ), 'https://proxy.lan:80')
        self.assertEqual(format_proxy(
            '', 'user', '', 'proxy.lan', 0
            ), 'http://proxy.lan:80')
        self.assertEqual(format_proxy(
            '', '', 'password', 'proxy.lan', 0
            ), 'http://proxy.lan:80')
        self.assertEqual(format_proxy(
            '', 'user', 'password', 'proxy.lan', 0
            ), 'http://user:password@proxy.lan:80')
        self.assertEqual(format_proxy(
            '', '', '', 'proxy.lan', -1
            ), 'http://proxy.lan:80')
        self.assertEqual(format_proxy(
            '', '', '', 'proxy.lan', 8080
            ), 'http://proxy.lan:8080')

    def test_parse_uri(self):
        self.assertEqual(parse_uri(
            ''), (None, None))
        self.assertEqual(parse_uri(
            'mopidy'), (None, None))
        self.assertEqual(parse_uri(
            'mopidy:channel'), (None, None))
        self.assertEqual(parse_uri(
            'somafm:nothing'), ('nothing', ''))
        self.assertEqual(parse_uri(
            'somafm:channel:'), ('channel', ''))
        self.assertEqual(parse_uri(
            'somafm:channel:/path'), ('channel', 'path'))
        self.assertEqual(parse_uri(
            'somafm:chan:/path/extended'), ('chan', 'path/extended'))
