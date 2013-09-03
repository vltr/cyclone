#!/bin/bash

set -e
if [ ! -d /opt/pypy-1.9 ]
then
	echo /opt/pypy-1.9 not found.
	echo you must install it first.
	echo run: curl cyclone.io/install-pypy.sh \| bash
	exit 1
fi

pypy_pip install pyopenssl
pypy_pip install twisted
pypy_pip install cyclone

echo Linking /opt/pypy/bin/twistd -\> /usr/local/bin/pypy_twistd
ln -sf /opt/pypy/bin/twistd /usr/local/bin/pypy_twistd

echo Run cyclone: pypy_twistd cyclone --help
