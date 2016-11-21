import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


if sys.argv[-1] == 'publish':
    os.system('python setup.py register')
    os.system('python setup.py sdist upload')
    sys.exit()

setup(
    name="Confopy",
    version="0.4.11",
    url="https://github.com/ooz/Confopy",
    author="Oliver Zscheyge",
    author_email="oliverzscheyge@gmail.com",
    packages=["confopy", "confopy.analysis", "confopy.localization", "confopy.model", "confopy.pdfextract", "confopy.localization.de", "confopy.localization.de.corpus_de"],
    license="MIT License",
    description="Evaluates the linguistic and structural quality of scientific texts.",
    long_description=open("README.md").read(),
    package_dir={"confopy.model": "confopy/model"},
    package_data={"": ["README.md", "bin/confopy"],
                  "confopy.model": ["confopy_document.xsd"]},
    include_package_data=True,
    scripts=["bin/confopy"],
    data_files = ["README.md"],
    install_requires=[
        "lxml >= 3.3.5",
        "numpy == 1.6.2",
        "nltk >= 3.0.0",
        "Pattern == 2.6",
        "pyenchant == 1.6.5",
        "pdfminer == 20110515",
    ],
)
# formerly used lxml 2.3.2
# pyenchant is for spell checking
# other maybe deps:
#"pyyaml ==",
