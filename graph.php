<?php

require_once 'buildorder.php';

$package_set = read_cmdline($argc, $argv);

$deps = getDepTree($package_set);

printGraph($deps, 'depgraph');
system('eog depgraph.dot.png');
