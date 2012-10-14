#!/usr/bin/php
<?php
require_once 'buildorder.php';
require_once 'pkgstatus.php';


$package_set = read_cmdline($argc, $argv);
$build_order = getBuildOrder($package_set);

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

echo "INSTALL:\n";
printArray($install);


echo "\n\nBUILD:\n";
printArray($build);

echo "\n\nKEEP:\n";
printArray($keep);

echo "\n\nMISSING:\n";
printArray($missing);

