#!/bin/bash
#
# Parses ABUILD and print requested variable
# Usage: ./get_abuild_var.sh VAR_NAME FILENAME
#
ABUILD="${1}"
( . "$ABUILD"
echo '{'
LAST=${@: -1}
for var in ${@:2}; do
    # TODO guess if array
    value=$(eval echo \$$var)
    echo -n '"'$var'": "'$value'"'
    [ "$LAST" != "$var" ] && echo ','
done
echo
echo '}'
)

