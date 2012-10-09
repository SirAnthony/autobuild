#!/bin/bash
# This script calls sqlite directly to find out what package version is installed
PKGNAME=$1
PKGVER=$(sqlite3 /var/mpkg/packages.db "SELECT package_version FROM packages WHERE package_installed=1 AND package_name=\"$PKGNAME\"")
[ "$PKGVER" = "" ] && exit 1
PKGBUILD=$(sqlite3 /var/mpkg/packages.db "SELECT package_build FROM packages WHERE package_installed=1 AND package_name=\"$PKGNAME\"")
PKGVER=$(echo $PKGVER | sed 's/_[git|hg|svn].*//g')
echo ${PKGVER}-${PKGBUILD}

