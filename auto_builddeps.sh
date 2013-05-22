#!/bin/bash

ABUILD_PATH=${ABUILD_PATH:-${HOME}/abuilds}

get_deps() {
    # Get package deps via API
    URL=http://api.agilialinux.ru/dep/$1
    wget -O - $URL 2>/dev/null
}

add_deps() {
    AB_NAME=$ABUILD_PATH/$1/ABUILD

    LINENUM="$(grep -n 'tags=' $AB_NAME | sed 's/:.*//g')"
    LINESUM=$(cat $AB_NAME | wc -l)
    AB_TMP=${AB_NAME}.tmp
    L=0
    cat $AB_NAME | head -n $LINENUM | grep -v '^[^#]*build_deps=' > $AB_TMP
    echo "" >> $AB_TMP
    echo "# Automatically-generated build_deps. Subject to revision." >> $AB_TMP
    echo 'build_deps="'$2'"' >> $AB_TMP
    cat $AB_NAME | tail -n $(expr $LINESUM - $LINENUM) | grep -v '^[^#]*build_deps='  >> $AB_TMP
    mv $AB_TMP $AB_NAME
}


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
        DEPS=$(get_deps $i)
        echo "$i: no build_deps, should be: $DEPS"
        if [ "$AUTOADD" == "1" ] ; then
            add_deps $i "$DEPS"
        fi
    fi
done

