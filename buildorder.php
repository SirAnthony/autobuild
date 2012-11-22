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
	$new_size = count($deps);
	while ($old_size!=$new_size) {
		foreach($deps as $pkgname => $pkgdeps) {
			foreach($pkgdeps as $p) {
				if (isset($deps[$p])) continue;
				$d = get_builddeps($ABUILD_PATH . '/' . $p . '/ABUILD');
				if (count($d)==0) $d = get_deps($p);
				$deps[$p] = $d;
			}
		}
		$old_size = $new_size;
		$new_size = count($deps);
	}
	return $deps;
}


// Initialize build order with zero-depended packages
function initBuildOrder($deps) {
	$build_order = array();
	foreach($deps as $pkgname => $dep ) {
		if (trim($pkgname==='')) continue;
		if (count($dep)==0) {
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
		$kl = mergePackageSet($kl);
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
function tryEnqueuePackage($pkgname, $dep, $build_order) {
	if (inQueue($pkgname, $build_order)) {
		return false;
	}
	foreach($dep as $d) {
		if (!inQueue($d, $build_order)) {
			$can_add = false;
			debug("DEP FAIL: $pkgname => $d\n");
			return false;
		}
		debug("DEP OK: $pkgname => $d\n");
	}
	debug("ALL DEPS OK: Adding $pkgname\n\n");
	return true;
}

// FIXME: calculateInQueue and extractLoop does almost the same. Should we merge it together?
function calculateInQueue($deps, $build_order, &$not_enqueued = NULL) {
	$in_queue = count($deps);
	foreach($deps as $pkgname => $dep) {
		if (inQueue($pkgname, $build_order)) $in_queue--;
		else if ($not_enqueued!==NULL) $not_enqueued[] = $pkgname;
	}
	return $in_queue;
}

function isResolvableBy($checklist, $deps, $processed_packages) {
	foreach($checklist as $check_pkgname) {	
		$found = false;
		foreach($deps as $pkgname => $dep) {
			if ($check_pkgname!==$pkgname) continue;
			$found = true;
			if (inQueue($pkgname, $processed_packages)) continue;
			// Do something
			if (!tryEnqueuePackage($pkgname, $dep, $processed_packages)) return false;
			break;
		}
		if (!$found) {
			die("FATAL: $check_pkgname not found within deps\n");
		}
	}
	return true;
}

function getCombinedCheckList($build_order, $loop_register_data) {
	$ret = $build_order;
	for ($i=0; $i<count($loop_register_data); $i++) {
		if ($loop_register_data[$i]===NULL) continue;
		$ret = array_merge($ret, $loop_register_data[$i]['order']);
	}
	return array_unique($ret);
}

function tryAdvanceLoops(&$build_order, $deps, &$loop_register_data) {
	$ret = 0;
	for ($i=0; $i<count($loop_register_data); $i++) {
		if ($loop_register_data[$i]===NULL) continue; // Means already processed item
		$loop_order = $loop_register_data[$i]['order'];
		$stuck_position = $loop_register_data[$i]['pos'];
		// Check if loop_order is resolvable by $build_order and $loop_order
		if (isResolvableBy($loop_order, $deps, array_merge($build_order, $loop_order))) {
			/* DEBUG */
			/*
			echo "\n\n\n-----------Loop order detected to be resolvable. Loop itself:---------\n";
			printArray($loop_order);
			echo "===========================Build_order:===================================\n";
			printArray($build_order); 
			echo "----------------------------------------------------------------------------\n\n\n";
			 */
			$merge_position = count($build_order);
			foreach($loop_order as $pkgname) {
				$build_order[] = $pkgname;
				$ret++;
			}
			// Re-add packages that were between
			for ($z=$stuck_position; $z<$merge_position; $z++) {
				$build_order[] = $build_order[$z];
				$ret++;
			}
			echo "Finished loop $i\n";
			$loop_register_data[$i] = NULL; // Unregister loop
		}
	}
	return $ret;
			
}

// Main function: builds build order
function resolve($deps) {
	// Initialize build order with packages that have zero dependencies
	$build_order = initBuildOrder($deps);

	// Initializing counters (used to detect loops)
	$old_size = count($build_order);
	$new_size = count($build_order);

	// Loop registration storage
	$loop_register_data = array();
	$step = 0;

	// Main cycle: looping over packages while queue is not empty
	while (calculateInQueue($deps, $build_order)>0) {
		$step++;
		echo "Step $step/part 0, in queue: " . calculateInQueue($deps, $build_order) . " packages, enqueued: " . count($build_order) . "\n";
		// Checking each package if it is ready to be added to build_order.
		// It means that it is:
		// 	1) not in build_order already,
		// 	2) all of his deps are already there
		// If success, package is added to $build_order
		// If not, just skip it
		$this_move = false;
		$step_move = 0;
		foreach($deps as $pkgname => $dep) {
			$check_array = getCombinedCheckList($build_order, $loop_register_data);
			if (tryEnqueuePackage($pkgname, $dep, $check_array)) {
				$build_order[] = $pkgname;
				$this_move = true;
				$step_move++;
			}
		}
		if ($step_move>0) echo "Part 1: move $step_move\n";
		echo "Step $step/part 1 (direct add), in queue: " . calculateInQueue($deps, $build_order) . " packages, enqueued: " . count($build_order) . "\n";

		// At this point, try to advance with loops
		$loop_move = tryAdvanceLoops($build_order, $deps, $loop_register_data);
		if ($loop_move>0) {
			$this_move = true;
			echo "Part 2 (LOOP): move $loop_move\n";
		}

		// Checking counters: we need to find out is there any advance in previous step

		// If old and current sizes match - no advance was made.
		// It means, that we are stuck on a dependency loop
		if (!$this_move) {
			// Get list of packages that remains unprocessed. By now, we don't know which of them forms a dependency loop
			$loop = extractLoop($deps, $build_order);
			
			// Debyg check (catches a case when in_queue is calculated incorrectly
			if (count($loop)==0) {
				die("CODE ERROR: Loop detected, but no loop really exist\n");
			}

			// Find a known loop which contains at least one of stucked packages
			$loop_order = findKnownLoopFor($loop);

			// Check if such known loop found
			if (!$loop_order) {
				printArray($loop);
				die("Unresolvable loop detected, fix known loops and try again");
			}

			echo "Registering loop: was " . count($loop_register_data) . ", ";
			$l['order'] = $loop_order;
			$l['pos'] = count($build_order);
			$loop_register_data[] = $l;
			echo "became : " . count($loop_register_data) . "\n";
			$this_move = true;
			
		}
		if (!$this_move) {
			$unprocessed_packages = array();
			$stuck_size = calculateInQueue($deps, $build_order, $unprocessed_packages);
			printArray($unprocessed_packages);
			die("Unresolvable loop within known loops, still unprocessed: $stuck_size\n");
		}
		$old_size = count($build_order);

		echo "Step $step/part 2 (loop processing), in queue: " . calculateInQueue($deps, $build_order) . " packages, enqueued: " . count($build_order) . "\n";
	}
	return $build_order;
}
function mergePackageSet($package_set) {
	$package_set = array_unique($package_set);
	for ($i=0; $i<count($package_set); $i++) {
		$newdata = getCorePackage($package_set[$i]);
		if ($package_set[$i]!==$newdata) {
			$package_set[$i] = $newdata;
		}
	}
	return array_unique($package_set);

}
function mergeMultiPackages($deps) {
	// First: get list of all packages mentioned in tree
	$list = array();

	foreach($deps as $package => $dep) {
		if (!isset($list[$package])) {
			$list[$package] = getCorePackage($package);
		}
		foreach($dep as $d) {
			if (!isset($list[$d])) {
				$list[$d] = getCorePackage($d);
			}
		}
	}
	// Disassemble
	$tmp = array();
	foreach($deps as $package => $dep) {
		$tmpd = array();
		foreach($dep as $d) {
			$tmpd[] = $list[$d];
			if ($list[$d]=='kernel-headers') die("BAD: " . __LINE__ . "\n");
		}
		$tmpd = array_unique($tmpd);
		$tmp[$list[$package]] = $tmpd;
		if ($list[$package]=='kernel-headers') die("BAD: " . __LINE__ . "\n");
	}
	return $tmp;
	/*$ret = array();
	foreach ($deps as $package => $dep) {
		for ($i=0; $i<count($dep); $i++) {
			$dep[$i] = $list[$dep[$i]];
		}
		$ret[$list[$package]] = $dep;
	}
	return $ret;*/
}

function getDepTree($package_set) {
	global $ABUILD_PATH;
	$deps = array();
	foreach ($package_set as $arg) {
		$d = get_builddeps($ABUILD_PATH . '/' . $arg . '/ABUILD');
		if (count($d)==0) $d = get_deps($arg);
		$deps[$arg] = $d;
	}

	$deps = expandDeps($deps);
	return $deps;

}

function getBuildOrder($package_set) {
	// First: merge package set
	echo "Merging requested packages...\n";
	$package_set = mergePackageSet($package_set);
	echo "Loading abuilds, this can take a time...\n";
	$deps = getDepTree($package_set);
	echo "Merging subpackages...\n";
	// Always merge multipackages. From now, this is mandatory.
	$deps = mergeMultiPackages($deps);
	echo "Calculating deps...\n";
	$build_order = resolve($deps);
	return $build_order;

}

function run($argc, $argv) {
	$package_set = read_cmdline($argc, $argv);
	$build_order = getBuildOrder($package_set);


	printArray($build_order);


}


//run($argc, $argv);
