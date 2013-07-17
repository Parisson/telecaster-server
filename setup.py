# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

CLASSIFIERS = ['Environment :: Web Environment', 'Framework :: Django', 'Intended Audience :: Science/Research', 'Intended Audience :: Education', 'Programming Language :: Python', 'Programming Language :: JavaScript', 'Topic :: Internet :: WWW/HTTP :: Dynamic Content', 'Topic :: Internet :: WWW/HTTP :: WSGI :: Application', 'Topic :: Multimedia :: Sound/Audio', 'Topic :: Multimedia :: Sound/Audio :: Analysis', 'Topic :: Multimedia :: Sound/Audio :: Players', 'Topic :: Scientific/Engineering :: Information Analysis', 'Topic :: System :: Archiving',  ]

setup(
  name = "telecaster-server",
  url = "https://github.com/yomguy/telecaster-server",
  description = "Live audio and video recording and streaming system based on Gstreamer, JACK, Vncserver and Fluxbox",
  long_description = open('README.rst').read(),
  author = "Guillaume Pellerin",
  author_email = "yomguy@parisson.com",
  version = '0.8',
  install_requires = [
        'deefuzzer',
  ],
  platforms=['OS Independent'],
  license='CeCILL v2',
  classifiers = CLASSIFIERS,
  packages = find_packages(),
  include_package_data = True,
  zip_safe = False,
)

import tcserver
tcserver.install.run()


