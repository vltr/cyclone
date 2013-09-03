#!/bin/bash

set -e
shopt -s expand_aliases
alias curl="curl -L --progress-bar"

function _install()
{
	if [ -d /opt/pypy-1.9 ]
	then
		echo pypy-1.9 is already installed
		echo remove /opt/pypy-1.9 and try again
		exit 1
	fi

	echo Downloading $1
	echo Decompressing in /opt/pypy-1.9
	curl $1 | tar jxf - -C /opt

	echo Linking /opt/pypy-1.9 -\> /opt/pypy
	cd /opt
	ln -sf pypy-1.9 pypy

	echo Linking /opt/pypy/bin/pypy -\> /usr/local/bin
	ln -sf /opt/pypy/bin/pypy /usr/local/bin

	echo Installing distribute \(easy_install\)
	echo Output log is in /tmp/python-distribute.log
	cd /tmp
	curl http://python-distribute.org/distribute_setup.py|pypy &> python-distribute.log
	rm -f distribute-*.tar.gz

	echo Installing pip
	curl https://raw.github.com/pypa/pip/master/contrib/get-pip.py|pypy

	echo Linking /opt/pypy/bin/pip -\> /usr/local/bin/pypy_pip
	ln -sf /opt/pypy/bin/pip /usr/local/bin/pypy_pip

	echo Installing virtualenv
	pypy_pip install virtualenv

	echo Linking /opt/pypy/bin/virtualenv -\> /usr/local/bin/pypy_virtualenv
	ln -sf /opt/pypy/bin/virtualenv /usr/local/bin/pypy_virtualenv

	echo Use: pypy_virtualenv -p pypy name
	echo Install cyclone: curl cyclone.io/install-pypy-cyclone.sh \| bash
}

case `uname -sm` in
	"Darwin x86_64")
		_install https://bitbucket.org/pypy/pypy/downloads/pypy-1.9-osx64.tar.bz2
		;;
	"Linux x86_64")
		_install https://bitbucket.org/pypy/pypy/downloads/pypy-1.9-linux64.tar.bz2
		;;
	"Linux i686"|"Linux i386")
		_install https://bitbucket.org/pypy/pypy/downloads/pypy-1.9-linux.tar.bz2
		;;
esac
