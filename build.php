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
	$arg = '';
	foreach($install as $i) {
		$arg .= $i . ' ';
	}
	passthru("mpkg-install $arg");
}

function buildPackages($build) {
	global $ABUILD_PATH;
	foreach($build as $b) {
		passthru("cd $ABUILD_PATH/$b && mkpkg", $ret);
	}
}

$package_set = read_cmdline($argc, $argv);
list($install, $build, $keep, $missing) = getBuildInstructions($package_set);
printBuildInstructions($install, $build, $keep, $missing);

if (sizeof($missing)>0) die("Errors detected: missing " . sizeof($missing) . " packages, cannot continue\n");

$do = getenv('DO_BUILD');
if ($do==="YES") {
	installPackages($install);
	buildPackages($build);
}
