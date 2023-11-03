from setuptools import setup, find_packages

PKG = "scilif_cnc_programmer"

VER = "0.0.1"
DESCRIPTION = "SCILIF production tool for PIC programming over CNC"
AUTHOR = "Ladislav Štefka"
AUTHOR_EMAIL = "stefka.lad@gmail.com"
URL = "https://www.scilif.com/"

with open("requirements.txt", "r") as req_file:
    REQUIREMENTS = req_file.read().splitlines()

with open("README.md", "r", encoding="utf-8") as readme_file:
    LONG_DESCRIPTION = readme_file.read()


setup(
    package_dir = {"": "src"}
    name=PKG,
    version=VER,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url=URL,
    packages=[PKG],
    install_requires=REQUIREMENTS,
    entry_points={
        'console_scripts': ['scilif_cnc_programmer=app.cnc_programmer.main:main'],
    },
    packages=find_packages(),
    install_requires=REQUIREMENTS,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.7, <4",
)