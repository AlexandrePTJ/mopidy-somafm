*************
Mopidy-SomaFM
*************

.. image:: https://img.shields.io/pypi/v/Mopidy-SomaFM
    :target: https://pypi.org/project/Mopidy-SomaFM/
    :alt: Latest PyPI version

.. image:: https://img.shields.io/circleci/build/gh/AlexandrePTJ/mopidy-somafm
    :target: https://circleci.com/gh/AlexandrePTJ/mopidy-somafm
    :alt: CircleCI build status

.. image:: https://img.shields.io/codecov/c/gh/AlexandrePTJ/mopidy-somafm
    :target: https://codecov.io/gh/AlexandrePTJ/mopidy-somafm
    :alt: Test coverage

SomaFM extension for Mopidy


Installation
============


Debian/Ubuntu
-------------

Install by running::

    python3 -m pip install Mopidy-SomaFM

Or, if available, install the Debian/Ubuntu package from
`apt.mopidy.com <https://apt.mopidy.com/>`_.


Configuration
=============

Before starting Mopidy, you must add configuration for
Mopidy-SomaFM to your Mopidy configuration file::

    [somafm]
    encoding = aac
    quality = highest

- ``encoding`` must be either ``aac``, ``mp3`` or ``aacp``
- ``quality`` must be one of ``highest``, ``fast``, ``slow``, ``firewall``

If the preferred quality is not available for a channel, the extension will fallback
to ``fast``. And afterwards if the preferred encoding is not available for that
quality, it will fallback to using ``mp3``.
It seems that all channels support the combination ``fast`` + ``mp3``

You can also choose to use the channel DJ as the reported track artist (default behavior)::

    [somafm]
    dj_as_artist = true


Project resources
=================

- `Source code <https://github.com/AlexandrePTJ/mopidy-somafm>`_
- `Issue tracker <https://github.com/AlexandrePTJ/mopidy-somafm/issues>`_
- `Changelog <https://github.com/AlexandrePTJ/mopidy-somafm/blob/master/CHANGELOG.rst>`_


Credits
=======

- Original author: `Alexandre Petitjean <https://github.com/AlexandrePTJ>`__
- Current maintainer: `Alexandre Petitjean <https://github.com/AlexandrePTJ>`__
- `Contributors <https://github.com/AlexandrePTJ/mopidy-somafm/graphs/contributors>`_
