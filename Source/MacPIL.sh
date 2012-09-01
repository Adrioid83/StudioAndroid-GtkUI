#!/usr/bin/env sh

if [ "$1" = "1" ]
then
	pip install PIL
fi

if [ "$?" != "0" ]
then
	ARCHFLAGS="-arch i386 -arch x86_64" pip install PIL
fi

return "$?"
