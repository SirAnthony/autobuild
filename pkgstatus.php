<?php
require_once 'config.php';
/* This file contains functions to determine package status according to package-action.dia diagram. */


function isForcedToRebuild($pkgname, $force_array) {
	foreach($force_array as $f) {
		if ($f===$pkgname) return true;
	}
	return false;
}

function isInstalled($pkgname) {
	$handle = popen("./get_installed_version.sh $pkgname");
	$data = fread($handle, 65536);
	pclose($handle);
	if (trim(preg_replace("/\n/", '', $data))=="") return false;
	return true;
}

function isAvailable($pkgname) {
	$handle = popen("./get_available_versions.sh $pkgname");
	$data = fread($handle, 65536);
	pclose($handle);
	if (trim(preg_replace("/\n/", '', $data))=="") return false;
	return true;
}

function isAbuildEsists($pkgname) {
	if (file_exists($ABUILD_PATH . '/' . $pkgname . '/ABUILD')) return true;
	return false;
}

function isCanBeBuilt($pkgname) {
	// Temporarily, assume that any package can be built
	return true;
}


