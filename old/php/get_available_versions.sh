#!/bin/bash
# This script calls sqlite directly to find out what package versions are available
PKGNAME=$1
PKGVER=$(sqlite3 /var/mpkg/packages.db "SELECT package_version, package_build FROM packages WHERE package_name=\"$PKGNAME\"")
[ "$PKGVER" = "" ] && exit 1
echo ${PKGVER}

