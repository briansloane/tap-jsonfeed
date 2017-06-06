#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='tap-jsonfeed',
      version='0.1.0',
      description='Singer.io tap for extracting data from a JSON Feed',
      author='Brian Sloane',
      url='http://singer.io',
      classifiers=['Programming Language :: Python :: 3 :: Only'],
      py_modules=['tap_jsonfeed'],
      install_requires=['singer-python==1.6.0a2',
                        'requests==2.13.0'],
      entry_points='''
          [console_scripts]
          tap-jsonfeed=tap_jsonfeed:main
      ''',
      packages=['tap_jsonfeed'],
      package_data = {
          'tap_jsonfeed': [
              'feed.json'
              ]
          }
)
