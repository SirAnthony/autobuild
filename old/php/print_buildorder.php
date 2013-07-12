#!/usr/bin/php
<?php
require_once 'buildorder.php';

$package_set = read_cmdline($argc, $argv);
$build_order = getBuildOrder($package_set);

printArray($build_order);
