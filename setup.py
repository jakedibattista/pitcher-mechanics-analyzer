from setuptools import setup, find_packages

setup(
    name="pitcher-analyzer",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'google-cloud-videointelligence',
        'google-cloud-aiplatform',
        'pandas',
    ],
) 