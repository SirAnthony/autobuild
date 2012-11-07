#!/bin/bash
ABUILD="$1"

( . "$ABUILD"
	echo "$pkgname"
)

