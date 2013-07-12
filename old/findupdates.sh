#!/bin/bash
#
# Finds abuilds for installed packages that have versions not equal to installed ones

ABUILD_DIR=${ABUILD_DIR:-${HOME}/abuilds}

get_abuild_var() {
	VARNAME="$1"
	ABUILD="$2"

	( . "$ABUILD"
		echo ${!VARNAME}
	)
}


for i in $(find ${ABUILD_DIR} -name ABUILD) ; do
	ABUILD_DIRNAME=$(dirname $i)
	ABUILD_BASENAME=$(basename ${ABUILD_DIRNAME})

	ABUILD_NAME=$(get_abuild_var pkgname $i)

	# Skip non-primary packages
	if [ "${ABUILD_NAME}" != "${ABUILD_BASENAME}" ] ; then
		continue
	fi

	ABUILD_VER=$(get_abuild_var pkgver $i)
	ABUILD_BUILD=$(get_abuild_var pkgbuild $i)

	# Get installed version. In future, this should refer to latest built one, not nessecarily installed
	INSTALLED_VER=$(./get_installed_version.sh $ABUILD_NAME)

	if [ "$INSTALLED_VER" == "" ] ; then
		# No installed version, skip it
		continue;
	fi

	if [ "$INSTALLED_VER" == "${ABUILD_VER}-${ABUILD_BUILD}" ] ; then
		# Versions matches, skip it
		continue;
	fi

	# If we are here, then versions does not match
	if [ -z $CLEAN_OUTPUT ] ; then
		echo "$ABUILD_NAME: $ABUILD_VER-$ABUILD_BUILD (abuild) vs $INSTALLED_VER (installed)"
	else
		echo $ABUILD_NAME
	fi
done

