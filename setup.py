from setuptools import setup, find_packages

setup(
    name="pitcher_analyzer",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "streamlit",
        "opencv-python",
        "numpy",
        "google-generativeai",
        # ... other dependencies ...
    ],
) 