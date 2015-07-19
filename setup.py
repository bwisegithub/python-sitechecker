""" Set up python-sitechecker.
"""
from codecs import open
from setuptools import setup, find_packages
from os import path


THIS_PATH = path.abspath(path.dirname(__file__))


# Get the long description from README.md
with open(path.join(THIS_PATH, 'README.md'), encoding='utf-8') as f:
    THIS_LONG_DESCRIPTION = f.read()


setup(
    name='python-sitechecker',
    version='1.0.1',
    description='Tool for checking security, page speed, and code '\
        'validation for URL(s)',
    long_description=THIS_LONG_DESCRIPTION,
    url='https://github.com/bwisegithub/python-sitechecker',
    author='bwisegithub',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Natural Language :: English',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 2.7.6',
        'Topic :: Internet :: WWW/HTTP :: Site Management'
    ],
    keywords='wot, sucuri, google pagespeed, w3 validation, '\
        'site reputation, server location, site security, malware scan, '\
        'external links, css validation',
    install_requires=['BeautifulSoup4', 'requests', 'requests[security]'],
    packages=find_packages(exclude=['tests']),
    zip_safe=True
)
