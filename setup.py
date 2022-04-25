from setuptools import setup, find_packages

setup(
    name='Zyte SmartProxy Selenium',
    version='1.0.0',
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
