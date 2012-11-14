#!/bin/bash
ABUILD_PATH=/home/aix/abuilds
for i in $@ ; do
	FILE="$ABUILD_PATH/$i/ABUILD"
	if [ ! -f "$FILE" ] ; then
		echo "$i: No ABUILD"
		continue
	fi

	BD="$(./get_abuild_var.sh build_deps $FILE)"
	TAGS="$(./get_abuild_var.sh tags $FILE | grep virtual)"

	if [ "$TAGS" != "" ] ; then
		# Virtual packages does not have any build deps, skip it
		continue
	fi

	if [ "$BD" == "" ] ; then
		echo "$i: no build_deps"
	fi
done
