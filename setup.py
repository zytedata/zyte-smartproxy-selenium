from setuptools import setup, find_packages
from zyte_smartproxy_selenium import __version__

setup(
    name='Zyte SmartProxy Selenium',
    version=__version__,
    packages=find_packages(),
    install_requires=[
        'adblockparser>=0.7',
        'requests>=2.27',
        'selenium-wire>=4.6',
    ],
    python_requires='>=3.6',
    description='A wrapper over Selenium Wire to provide Zyte Smart Proxy Manager specific functionalities.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/zytedata/zyte-smartproxy-selenium',
)
