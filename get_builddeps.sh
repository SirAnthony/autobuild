#!/bin/bash

ABUILD="$1"

( . "$ABUILD"
	echo ${build_deps}
)

