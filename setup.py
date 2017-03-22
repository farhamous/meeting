import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

requires = [
    'SQLAlchemy',
    'python_telegram_bot'
    ]


setup(name='meeting',
      version='0.0',
      description='meeting telegram bot',
      long_description='meeting telegram bot',
      classifiers=[
          "Programming Language :: Python",
          "Framework :: python_telegram_bot",
      ],
      author='Farhad',
      author_email='farhad@gmail.com',
      url='',
      keywords='telegram bot python_telegram_bot meeting',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      )
