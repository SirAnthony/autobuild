#!/bin/bash
# 
# Parses ABUILD and print requested variable
# Usage: ./get_abuild_var.sh VAR_NAME FILENAME
# 

VARNAME="$1"
ABUILD="$2"

( . "$ABUILD"
	echo ${!VARNAME}
)

