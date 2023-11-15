#!/bin/bash

echo "build starts"
python3.9 -m pip install --upgrade pip
pip3 install -r requirements.txt
echo "build ends"

# Install MySQL development libraries
apt-get update
apt-get install -y libmysqlclient-dev
