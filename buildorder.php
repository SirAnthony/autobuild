<?php

require_once 'functions.php';
require_once 'config.php';

// Fill deps with command line arguments
function read_cmdline($argc, $argv) {
	$ret = array();
	for ($i=1; $i<$argc; $i++) {
		if (trim($argv[$i])==='') continue;
		$ret[] = $argv[$i];
	}
	return $ret;
}

// Expand deps: get dependencies of all dependencies and fill array with them
function expandDeps($deps) {
	global $ABUILD_PATH;
	$old_size = 0;
	$new_size = sizeof($deps);
	while ($old_size!=$new_size) {
		foreach($deps as $pkgname => $pkgdeps) {
			foreach($pkgdeps as $p) {
				if (isset($deps[$p])) continue;
				$d = get_builddeps($ABUILD_PATH . '/' . $p . '/ABUILD');
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
		if (trim($pkgname==='')) continue;
		if (sizeof($dep)==0) {
			$build_order[] = $pkgname;
		}
	}
	return $build_order;
}

// Reads all known loops
function getKnownLoops() {
	$dir = scandir('loops');
	foreach($dir as $loop_name) {
		if ($loop_name == '.' || $loop_name == '..') continue;
		$loop_resolve_data = file_get_contents('loops/' . $loop_name);
		$known_loop = explode("\n", $loop_resolve_data);
		$kl = array();
		foreach($known_loop as $k) {
			$filtered_k = trim(preg_replace('/#.*/', '', $k));
			if ($filtered_k==='') continue;
			$kl[] = $filtered_k;
		}
		$ret[$loop_name] = $kl;
	}
	return $ret;
}

// Find any known loop that can resolve at least one of stucked packages
function findKnownLoopFor($loop) {
	// Read an array of all known loops
	$known_loops = getKnownLoops();

	// Let's search which known loop can resolve at least one of out loop members
	// Going thru all known loops...
	foreach($known_loops as $known_loop_name => $known_loop_order) {
		// Going thru our stalled packages (provided to function)
		foreach($loop as $loop_item => $loop_item_deps) {
			// Going thru current known loop and find out
			foreach($known_loop_order as $loop_order_item) {
				// Check if this loop order contains this stucked package
				if ($loop_item===$loop_order_item) {
					// Yes, this is loop order rule that we need
					return $known_loop_order;
				}
			}
		}
	}
	// If we found nothing - return false.
	return false;
	

}

// Returns packages that were unprocessed
function extractLoop($deps, $build_order) {
	$loop = array();
	foreach($deps as $pkgname => $dep) {
		if (inQueue($pkgname, $build_order)) continue;
		$loop[$pkgname] = $dep;
	}
	return $loop;

}
function tryEnqueuePackage($pkgname, $add_pkgname, $dep, &$build_order, &$in_queue) {
	if (inQueue($pkgname, $build_order)) {
		if ($pkgname!==$add_pkgname && !inQueue($add_pkgname, $build_order)) {
			$build_order[] = $add_pkgname;
			$in_queue--;
		}
		return true;
	}
	$can_add = true;
	foreach($dep as $d) {
		if (!inQueue($d, $build_order)) {
			$can_add = false;
			break;
		}
		debug("DEP: $add_pkgname => $d\n");
	}
	if ($can_add) {
		debug("Adding $add_pkgname\n\n");
		$build_order[] = $add_pkgname;
		$in_queue--;
		return true;
	}
	return false;
}



// Main function: builds build order
function resolve($deps) {
	// Initialize build order with packages that have zero dependencies
	$build_order = initBuildOrder($deps);
	// Initializing counters (used to detect loops)
	$old_size = sizeof($build_order);
	$new_size = sizeof($build_order);
	$in_queue = sizeof($deps) - sizeof($build_order);
	$old_inqueue = $in_queue;

	// Main cycle: looping over packages while queue is not empty
	while ($in_queue>0) {
		// Checking each package if it is ready to be added to build_order.
		// It means that it is:
		// 	1) not in build_order already,
		// 	2) all of his deps are already there
		// If success, package is added to $build_order, and $in_queue reduces by 1.
		// If not, just skip it
		foreach($deps as $pkgname => $dep) {
			tryEnqueuePackage($pkgname, $pkgname, $dep, $build_order, $in_queue);
		}

		// Checking counters: we need to find out is there any advance in previous step
		$old_size = $new_size;
		$new_size = sizeof($build_order);

		// If old and current sizes match - no advance was made.
		// It means, that we are stuck on a dependency loop
		if ($old_size===$new_size) {
			// Get list of packages that remains unprocessed. By now, we don't know which of them forms a dependency loop
			$loop = extractLoop($deps, $build_order);
			
			// Debyg check (catches a case when in_queue is calculated incorrectly
			if (sizeof($loop)==0) {
				die("CODE ERROR: Loop detected, but no loop really exist\n");
			}

			// Find a known loop which contains at least one of stucked packages
			$loop_order = findKnownLoopFor($loop);

			// Check if such known loop found
			if (!$loop_order) {
				die("Unresolvable loop detected, fix known loops and try again");
				printArray($loop);
			}

			// If we found that known loop, add it completely in queue without any checking
			// FIXME: this is a really bad idea, since known loops may contain errors, be incomplete and so on.
			// What we, really, need to do, is:
			// 	1. Known loop order may be resolvable by itself - it means that it has no deps except itself and ones which are already processed. In that case, just add that loop without checking (this is a current behaviour for all cases)
			// 	2. Known loop order may have other unprocessed deps that were not specified inside a loop. We need to build these deps first, then build a loop, and then rebuild these deps again. Maybe, rebuild a loop again (not sure).

			foreach($loop_order as $pkgname) {
				$build_order[] = $pkgname;
			}
			
			// Adjust $in_queue variable
			foreach($loop as $loop_item => $loop_item_deps) {
				if (inQueue($loop_item, $loop_order)) $in_queue--;
			}
			
			$new_size = sizeof($build_order);

		}
		$old_inqueue = $in_queue;
	}
	return $build_order;
}

function mergeMultiPackages($deps) {
	// First: get list of all packages mentioned in tree
	$list = array();
	foreach($deps as $package => $dep) {
		if (!isset($list[$package])) $list[$package] = getCorePackage($package);
		foreach($dep as $d) {
			if (!isset($list[$d])) $list[$d] = getCorePackage($d);
		}
	}
	$ret = array();
	foreach ($deps as $package => $dep) {
		for ($i=0; $i<sizeof($dep); $i++) {
			$dep[$i] = $list[$dep[$i]];
		}
		$ret[$list[$package]] = $dep;
	}
	return $ret;
}

function getDepTree($package_set) {
	global $ABUILD_PATH;
	$deps = array();
	foreach ($package_set as $arg) {
		$d = get_builddeps($ABUILD_PATH . '/' . $arg . '/ABUILD');
		if (sizeof($d)==0) $d = get_deps($arg);
		$deps[$arg] = $d;
	}

	$deps = expandDeps($deps);
	return $deps;

}

function getBuildOrder($package_set) {
	$deps = getDepTree($package_set);
	// Always merge multipackages. From now, this is mandatory.
	$deps = mergeMultiPackages($deps);
	$build_order = resolve($deps);
	return $build_order;

}

function run($argc, $argv) {
	$package_set = read_cmdline($argc, $argv);
	$build_order = getBuildOrder($package_set);


	printArray($build_order);


}


//run($argc, $argv);
