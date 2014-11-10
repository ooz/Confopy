#!/bin/bash

export PYTHONPATH=$PYTHONPATH:./

python confopy/model/lines.py
python confopy/model/document.py

python confopy/test/test_pdfextract.py
