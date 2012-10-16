#!/usr/bin/php
<?php

require_once 'buildorder.php';

$package_set = read_cmdline($argc, $argv);

$deps = getDepTree($package_set);

printGraph($deps, 'depgraph', $package_set);
system('xdg-open depgraph.dot.png');
