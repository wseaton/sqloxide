# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sqloxide']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'sqloxide',
    'version': '0.1.1',
    'description': 'Python bindings for sqlparser-rs',
    'long_description': None,
    'author': 'Will Eaton',
    'author_email': 'me@wseaton.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/wseaton/sqloxide',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6.0,<4.0',
}
from build import *
build(setup_kwargs)

setup(**setup_kwargs)
