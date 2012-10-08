#!/bin/bash
# Finds abuilds for installed packages that have versions not equal to installed ones

ABUILD_DIR=${ABUILD_DIR:-${HOME}/abuilds}

for i in $(find ${ABUILD_DIR} -name ABUILD) ; do
	echo "Processing $i, dir: `pwd`"
	ABUILD_DIRNAME=$(dirname $i)

	ABUILD_NAME=$(./get_abuild_var.sh pkgver $i)
	ABUILD_VER=$(./get_abuild_var.sh pkgbuild $i)
	ABUILD_BUILD=$(./get_abuild_var.sh pkgname $i)

	INSTALLED_VER=$(./get_installed_version.sh $ABUILD_NAME)

	if [ "$INSTALLED_VER" == "" ] ; then
		# Not installed
		continue;
	fi

	if [ "$INSTALLED_VER" == "${ABUILD_VER}-${ABUILD_BUILD}" ] ; then
		# Versions match
		continue;
	fi

	# If we are here, versions does not match
	echo $ABUILD_NAME
done

