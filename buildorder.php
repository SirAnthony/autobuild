#!/usr/bin/php
<?php

require_once 'functions.php';


// Fill deps with command line arguments
function initCmdline($argc, $argv) {
	$deps = array();
	for ($i=1; $i<$argc; $i++) {
		$arg = $argv[$i];
		$d = get_builddeps('/home/aix/abuilds/' . $arg . '/ABUILD');
		if (sizeof($d)==0) $d = get_deps($arg);
		$deps[$arg] = $d;
	}
	return $deps;
}

// Expand deps: get dependencies of all dependencies and fill array with them
function expandDeps($deps) {
	$old_size = 0;
	$new_size = sizeof($deps);
	while ($old_size!=$new_size) {
		foreach($deps as $pkgname => $pkgdeps) {
			foreach($pkgdeps as $p) {
				if (isset($deps[$p])) continue;
				$d = get_builddeps($p);
				if (sizeof($d)==0) $d = get_deps($p);
				$deps[$p] = $d;
			}
		}
		$old_size = $new_size;
		$new_size = sizeof($deps);
	}
	return $deps;
}


// Initialize build order with zero-depended packages
function initBuildOrder($deps) {
	$build_order = array();
	foreach($deps as $pkgname => $dep ) {
		if (sizeof($dep)==0) {
			$build_order[] = $pkgname;
		}
	}
	return $build_order;
}
function resolveLoop($loop) {
	// Read known loop file
	$loop_resolve_data = file_get_contents('known_loop');
	if ($loop_resolve_data===FALSE) die("FAILED TO OPEN FILE");
	$known_loop = explode("\n", $loop_resolve_data);

	// Compare
	$loop_errors = 0;
	$first_loop_member = array();
	foreach($known_loop as $k) {
		$found = false;
		foreach($loop as $pkgname => $l) {
			if ($pkgname===$k) {
				$found = true;
				$first_loop_member[$pkgname] = $l;
				break;
			}
		}
		if ($found) {
			break;
		}
	}
	return $first_loop_member;
}

function extractLoop($deps, $build_order) {
	$loop = array();
	foreach($deps as $pkgname => $dep) {
		if (inQueue($pkgname, $build_order)) continue;
		$loop[$pkgname] = $dep;
	}
	return $loop;

}

function resolve($deps, $build_order) {
	$old_size = sizeof($build_order);
	$new_size = sizeof($build_order);
	$in_queue = sizeof($deps) - sizeof($build_order);
	$old_inqueue = $in_queue;
	$loop_storages = array();
	while ($in_queue>0) {
		foreach($deps as $pkgname => $dep) {
			if (inQueue($pkgname, $build_order)) continue;
			$can_add = true;
			foreach($dep as $d) {
				if (!inQueue($d, $build_order)) {
					$can_add = false;
					break;
				}
			}
			if ($can_add) {
				$build_order[] = $pkgname;
				$in_queue--;
			}
		}
		// If we have a loop storage, try to add it again
		for ($i=0; $i<sizeof($loop_storages); $i++) {
			$loop_storage = $loop_storages[$i];
			if (sizeof($loop_storage)==0) continue;
			foreach($loop_storage as $pkgname => $dep) {
				$can_add = true;
				foreach($dep as $d) {
					if (!inQueue($d, $build_order)) {
						$can_add = false;
						break;
					}
				}
				if ($can_add) {
					$build_order[] = $pkgname;
					$loop_storages[$i] = array();
				}
			}
		}
		
		$old_size = $new_size;
		$new_size = sizeof($build_order);
		if ($old_size===$new_size) {
			// Loop detected
			$loop = extractLoop($deps, $build_order);
			$loop_order = resolveLoop($loop);
			$loop_storages[] = $loop_order;
			foreach($loop_order as $pkgname => $pkgdep) {
				$build_order[] = $pkgname;
				$in_queue--;
			}
			$new_size = sizeof($build_order);
		}
		if ($in_queue === $old_inqueue) {
			echo "Queue freeze, in queue: " . $in_queue. " packages, deps: " . sizeof($deps) . ", ordered: " . sizeof($build_order) . "\n";
			foreach($deps as $pkgname => $dep) {
				if (inQueue($pkgname, $build_order)) continue;
				echo "Frozen: $pkgname\n";
			}
			break;
		}
		$old_inqueue = $in_queue;
	}
	return $build_order;
}


function run($argc, $argv) {
	$deps = initCmdline($argc, $argv);
	$deps = expandDeps($deps);

	$build_order = initBuildOrder($deps);
	$build_order = resolve($deps, $build_order);

	printArray($build_order);


}


run($argc, $argv);
