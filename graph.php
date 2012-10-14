#!/usr/bin/php
<?php

require_once 'buildorder.php';

$package_set = read_cmdline($argc, $argv);

$deps = getDepTree($package_set);

printGraph($deps, 'depgraph');
system('xdg-open depgraph.dot.png');
