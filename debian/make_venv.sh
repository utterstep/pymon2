#!/bin/bash

virtualenv --python=python2 $1
. $1/bin/activate
pip install -r requirements.txt
deactivate
