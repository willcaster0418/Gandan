#!/bin/bash
#pip install setuptools wheel
#pip install twine
python3 setup.py sdist bdist_wheel
python3 -m twine upload dist/*
rm -rf gandan.egg-info
rm -rf dist
rm -rf build
