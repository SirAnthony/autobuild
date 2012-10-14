#!/bin/bash
ABUILD="$1"

( . "$ABUILD"
	if [ -z "$pkglist" ] ; then
		exit 0
	fi

	echo $pkgname
	for i in ${pkglist} ; do
		${i}
		echo $pkgname
	done
)

