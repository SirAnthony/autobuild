<?php
require_once 'config.php';
require_once 'functions.php';
/* This file contains functions to determine package status according to package-action.dia diagram. */


function isForcedToRebuild($pkgname, $force_array) {
	foreach($force_array as $f) {
		if ($f===$pkgname) {
			return true;
		}
	}
	return false;
}

function isInstalled($pkgname) {
	$handle = popen("./get_installed_version.sh $pkgname", 'r');
	$data = fread($handle, 65536);
	pclose($handle);
	if (trim(preg_replace("/\n/", '', $data))=="") {
		return false;
	}
	return true;
}

function isAvailable($pkgname) {
	$handle = popen("./get_available_versions.sh $pkgname", 'r');
	$data = fread($handle, 65536);
	pclose($handle);
	if (trim(preg_replace("/\n/", '', $data))=="") {
		return false;
	}
	return true;
}

function isAbuildEsists($pkgname) {
	global $ABUILD_PATH;
	if (file_exists($ABUILD_PATH . '/' . $pkgname . '/ABUILD')) {
		return true;
	}
	return false;
}

function isCanBeBuilt($pkgname) {
	// Temporarily, assume that any package can be built
	return true;
}

function getPackageAction($pkgname, $force_array) {
	if (isForcedToRebuild($pkgname, $force_array)) {
		if (isAbuildEsists($pkgname)) {
			if (isCanBeBuilt($pkgname)) {
				return 'build';
			}
			else {
				return 'fail';
			}
		}
		else {
			return 'fail';
		}
	}
	else {
		if (isInstalled($pkgname)) {
			return 'nothing';
		}
		else {
			if (isAvailable($pkgname)) {
				return 'install';
			}
			else {
				if (isAbuildEsists($pkgname)) {
					if (isCanBeBuilt($pkgname)) {
						return 'build';
					}
					else {
						return 'fail';
					}
				}
				else {
					return 'fail';
				}
			}
		}
	}

	// Being here means code failure.
	return FALSE;
}
