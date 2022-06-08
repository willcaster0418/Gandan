#!/bin/bash
PWD=`pwd`
echo $PWD

for path in `ls -d /usr/lib64/python*`
do
	ln -s $PWD $path/mw
done
