#!/bin/bash
python3 setup.py sdist upload -r pypi
python3.5 setup.py bdist_wheel --python-tag py35 upload -r pypi

#On windows: pynsist installer.cfg
# Done by appveyor
