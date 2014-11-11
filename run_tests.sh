#!/bin/bash

export PYTHONPATH=$PYTHONPATH:./:confopy/

python confopy/model/lines.py
python confopy/model/document.py

python confopy/analysis/analyzer.py

python confopy/test/test_pdfextract.py
