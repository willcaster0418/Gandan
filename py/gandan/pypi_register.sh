#!/bin/bash
#pip install setuptools wheel
#pip install twine
python3 setup.py sdist bdist_wheel
python3 -m twine upload dist/*
rm -f fury8208.egg-info/*
rmdir fury8208.egg-info/
rm -f dist/*