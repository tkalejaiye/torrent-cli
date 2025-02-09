from setuptools import setup, find_packages

setup(
    name="torrent-cli",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests>=2.31.0",
        "transmission-rpc>=7.0.11",
        "click>=8.1.7",
        "inquirer>=3.2.0",
    ],
    entry_points={
        "console_scripts": [
            "torrent-cli=torrent_cli:main",
        ],
    },
)
