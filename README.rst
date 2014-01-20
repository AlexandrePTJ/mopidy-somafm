*************
Mopidy-SomaFM
*************

.. image:: https://pypip.in/v/Mopidy-SomaFM/badge.png
    :target: https://pypi.python.org/pypi/Mopidy-SomaFM/
    :alt: Latest PyPI version

.. image:: https://pypip.in/d/Mopidy-SomaFM/badge.png
    :target: https://pypi.python.org/pypi/Mopidy-SomaFM/
    :alt: Number of PyPI downloads

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

The extension is enabled by default when installed and does not require any
configuration.

The extension requires that the Mopidy-Stream extension is enabled. It is
bundled with Mopidy and enabled by default, so it will be available unless
you've explicitly disabled it.

If you want to disable the extension, add the following to your Mopidy
configuration file::

    [somafm]
    enabled = false


Project resources
=================

- `Source code <https://github.com/AlexandrePTJ/mopidy-somafm>`_
- `Issue tracker <https://github.com/AlexandrePTJ/mopidy-somafm/issues>`_
- `Download development snapshot <https://github.com/AlexandrePTJ/mopidy-somafm/tarball/master#egg=Mopidy-SomaFM-dev>`_
