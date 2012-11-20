#!/usr/bin/php
<?php

require_once 'buildorder.php';
require_once 'pkgstatus.php';

function getBuildInstructions($package_set) {
	$build_order = getBuildOrder($package_set);
	if ($build_order == FALSE) {
		die("Ordering failed\n");
	}

	// Place packages according to it's action types
	$install = array();
	$build = array();
	$keep = array();
	$missing = array();

	foreach($build_order as $b) {
		$action = getPackageAction($b, $package_set);
		if ($action===FALSE) die($b . " status detection failed, got $action\n");

		switch($action) {
		case 'fail': $missing[] = $b; break;
		case 'install': $install[] = $b; break;
		case 'nothing': $keep[] = $b; break;
		case 'build': $build[] = $b; break;
		default: die($b . " status detection failed, got $action\n");
		}
	}
	$install = filterDupes($install);
	$keep = filterDupes($keep);
	$missing = filterDupes($missing);
	return array($install, $build, $keep, $missing);
}
function printBuildInstructions($install, $build, $keep, $missing) {


	echo "INSTALL:\n";
	printArray($install);


	echo "\n\nBUILD:\n";
	printArray($build);

	echo "\n\nKEEP:\n";
	printArray($keep);

	echo "\n\nMISSING:\n";
	printArray($missing);
	echo "-----\n";
}

function installPackages($install) {
	if (sizeof($install)==0) return;
	$arg = '';
	foreach($install as $i) {
		$arg .= $i . ' ';
	}
	passthru("mpkg-install -y $arg");
}

function buildPackages($build) {
	global $ABUILD_PATH;
	$counter = 0;
	$total = sizeof($build);

	if (getenv('AUTOBUILD_LOG')) file_put_contents(getenv('AUTOBUILD_LOG'), "Build started at " . date('Y:m:d H:i:s') . "\n\n", FILE_APPEND); 
	$start_from = getenv("START_FROM");
	if ($start_from == FALSE) $skip = 0;
	foreach($build as $b) {
		if ($counter<$start_from) {
			$counter++;
			continue;
		}
		if (getenv('AUTOBUILD_LOG')) file_put_contents(getenv('AUTOBUILD_LOG'), "[$counter/$total] $b: building...", FILE_APPEND); 
		passthru("cd $ABUILD_PATH/$b && mkpkg -si", $ret);
		if ($ret!=0) {
			if (getenv('AUTOBUILD_LOG')) file_put_contents(getenv('AUTOBUILD_LOG'), "FAILED at " . date('Y:m:d H:i:s') . "\n", FILE_APPEND);
			if (!getenv('SKIP_FAILED') || getenv('SKIP_FAILED')!=='YES') die("Package $b failed to build, stopping.\nSuccessfully built: $counter of $total packages.\n");
		}
		else {
			if (getenv('AUTOBUILD_LOG')) file_put_contents(getenv('AUTOBUILD_LOG'), "OK at " . date('Y:m:d H:i:s') . "\n", FILE_APPEND);
			$counter++;
		}
	}
}

$package_set = read_cmdline($argc, $argv);
echo "Calculating package build order for $argc packages, please wait...\n";
list($install, $build, $keep, $missing) = getBuildInstructions($package_set);
printBuildInstructions($install, $build, $keep, $missing);

if (sizeof($missing)>0 && getenv('IGNORE_MISSING')!=='YES') die("Errors detected: missing " . sizeof($missing) . " packages, cannot continue\n");

$do = getenv('DO_BUILD');
if ($do==="YES") {
	installPackages($install);
	buildPackages($build);
}
