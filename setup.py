"""Setup configuration for logsum package."""
from setuptools import setup, find_packages

setup(
    name="logsum",
    version="0.1.0",
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=[],
    entry_points={
        "console_scripts": [
            "logsum=src.logsum:main",
        ],
    },
)
