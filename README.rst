*************
Mopidy-SomaFM
*************

.. image:: https://pypip.in/v/Mopidy-SomaFM/badge.png
    :target: https://pypi.python.org/pypi/Mopidy-SomaFM/
    :alt: Latest PyPI version

.. image:: https://pypip.in/d/Mopidy-SomaFM/badge.png
    :target: https://pypi.python.org/pypi/Mopidy-SomaFM/
    :alt: Number of PyPI downloads

.. image:: https://travis-ci.org/AlexandrePTJ/mopidy-somafm.png?branch=master
    :target: https://travis-ci.org/AlexandrePTJ/mopidy-somafm
    :alt: Travis CI build status

.. image:: https://coveralls.io/repos/AlexandrePTJ/mopidy-somafm/badge.png?branch=master
   :target: https://coveralls.io/r/AlexandrePTJ/mopidy-somafm?branch=master
   :alt: Test coverage

`Mopidy <http://www.mopidy.com/>`_ extension for playing music from
`SomaFM <http://somafm.com/>`_.


Installation
============

Install by running::

    pip install Mopidy-SomaFM

Or, if available, install the Debian/Ubuntu package from `apt.mopidy.com
<http://apt.mopidy.com/>`_.


Configuration
=============

The extension requires that the Mopidy-Stream extension is enabled. It is
bundled with Mopidy and enabled by default, so it will be available unless
you've explicitly disabled it.

You may change prefered quality and encoding in your Mopidy configuration file::

    [somafm]
    encoding = aac
    quality = highest

- ``encoding`` must be either ``aac`` or ``mp3``
- ``quality`` must be one of ``highest``, ``fast``, ``slow``, ``firewall``


Warning
=======

SomaFM do not provide every possible combinaison of ``encoding`` and ``quality``.

In example, on the date of 2014/03/15, ``mp3 + highest`` gives only 3 playlists while ``aac + highest`` gives 14 and ``mp3 + highest`` gives 29.


Project resources
=================

- `Source code <https://github.com/AlexandrePTJ/mopidy-somafm>`_
- `Issue tracker <https://github.com/AlexandrePTJ/mopidy-somafm/issues>`_
- `Download development snapshot <https://github.com/AlexandrePTJ/mopidy-somafm/tarball/master#egg=Mopidy-SomaFM-dev>`_
