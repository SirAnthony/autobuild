#!/bin/bash
for i in $@ ; do
	BD=$(./get_abuild_var.sh build_deps /home/aix/abuilds/$i/ABUILD)
	if [ "$BD" == "" ] ; then
		echo "$i has no build_deps"
	fi
done
