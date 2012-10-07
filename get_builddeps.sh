#!/bin/bash
# 
# Parses ABUILD and print build_deps variable
# 

ABUILD="$1"

( . "$ABUILD"
	echo ${build_deps}
)

