#!/bin/bash
ABUILD="$1"

( . "$ABUILD"
	echo "$pkgname"
	if [ -z "$pkglist" ] ; then
		exit 0
	fi

	for i in ${pkglist} ; do
		"${i}"
		echo "$pkgname" >&1
	done
)

