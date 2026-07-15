"""Setup configuration for logsum package."""
from setuptools import setup

setup(
    name="logsum",
    version="0.1.0",
    packages=["src"],
    package_dir={"src": "src"},
    python_requires=">=3.7",
    install_requires=[],
    entry_points={
        "console_scripts": [
            "logsum=src.logsum:main",
        ],
    },
)
