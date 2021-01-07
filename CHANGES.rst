Changelog
=========


v2.0.1 (2021-01-07)
-------------------

- #37 Fix image display (Thanks to @dreamlayers and @morithil)


v2.0.0 (2020-03-11)
-------------------

- #36 Ready for Mopidy 3.0


v2.0.0rc1 (2019-12-04)
----------------------

- #32 Migrate to Python 3.7


v1.1.0 (2017-10-14)
-------------------

- #24: Graceful fallback
- #28: Various fix (DJ as artist, station ordering)


v1.0.1 (2016-01-19)
-------------------

- Use httpclient helper from Mopidy >= 1.1


v0.8.0 (2015-11-09)
-------------------

- #20: Replace HTTP with HTTPS for channels.xml


v0.7.1 (2015-01-04)
-------------------

- #11: Add Low Bitrate encoding (aacp)


v0.7.0 (2014-07-29)
-------------------

- #10: Remove playlists provider


v0.6.0 (2014-03-15)
-------------------

- Directly show PLS in browser
- Add precision about 'quality' and 'encoding' couple


v0.5.1 (2014-03-09)
-------------------

- Fix doc typo


v0.5.0 (2014-03-03)
-------------------

- #5: Select prefered quality and format from config
- Add tests and Travis-CI support


v0.4.0 (2014-02-16)
-------------------

- Add browse support for LibraryController


v0.3.1 (2014-01-30)
-------------------

- #3: Correct wrong subclassing


v0.3.0 (2014-01-29)
-------------------

- Require Mopidy >= 0.18
- Add proxy support for downloading SomaFM content
- #1: handle 'requests' exceptions
- Use builtin Mopidy's .pls support
- Internal code cleanup


v0.2.0 (2013-09-22)
-------------------

- PLS files are downloaded to local temp directory
- Implement library::lookup to allow adding tracks from playlist uri


v0.1.1 (2013-09-14)
-------------------

- Update Licence information


v0.1.0 (2013-09-13)
-------------------

- Initial release
- Create SomaFM extension for Mopidy
