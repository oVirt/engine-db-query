#!/bin/bash -xe
echo "Executing flake8 and building rpm"

set -xe

./autogen.sh
./configure
make -j5 rpm
