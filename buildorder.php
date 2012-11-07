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
// Get first element from loop, according to known loop list
function resolveLoop($loop) {
	$known_loops = getKnownLoops();
	// Let's search which known loop can resolve at lease some of out loop members
	// Since loop can contain packages that are not related to loop itself, it will be enough to find any of loop member and apply this loop
	foreach($known_loops as $loop_name => $loop_order) {
		foreach($loop as $loop_item => $loop_item_deps) {
			foreach($loop_order as $loop_order_item) {
				if ($loop_item===$loop_order_item) {
					// Yes, this is loop order rule that we need
					return $loop_order;
				}
			}
		}
	}
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
	$build_order = initBuildOrder($deps);
	$old_size = sizeof($build_order);
	$new_size = sizeof($build_order);
	$in_queue = sizeof($deps) - sizeof($build_order);
	$old_inqueue = $in_queue;
	while ($in_queue>0) {
		foreach($deps as $pkgname => $dep) {
			tryEnqueuePackage($pkgname, $pkgname, $dep, $build_order, $in_queue);
		}
				
		$old_size = $new_size;
		$new_size = sizeof($build_order);
		if ($old_size===$new_size) {
			// Loop detected
			$loop = extractLoop($deps, $build_order);
			if (sizeof($loop)==0) {
				die("CODE ERROR: Loop detected, but no loop really exist\n");
			}
			$loop_order = resolveLoop($loop);
			if ($loop_order==false) {
				debug("Stalled, maybe...\n");
				// Stalled? Try to resolve it
				$newloop = array();
				foreach($loop as $pkgname => $d) {
					$corename = getCorePackage($pkgname);
					debug("Trying $corename istead of $pkgname, in_queue: $in_queue\n");
					if (tryEnqueuePackage($corename, $pkgname, $d, $build_order, $in_queue)===false) {
						debug("Direct try failed, building newloop with $corename\n");
						$newloop[$corename] = $d;
					}
					else debug("Direct try success with $corename, in_queue: $in_queue\n");
				}
				if (sizeof($newloop)==sizeof($loop)) {
					debug("DIRECT RESOLVING FAILED\n");
					// Direct resolving failed, try loop methods again
					$loop = $newloop;
					$loop_order = resolveLoop($loop);
					if ($loop_order==false) {
						debug("Loop resolving failed\n");
						print_r($loop);
						echo "============";
						print_r($build_order);
						return false;
					}
				}
				else {
					// Reset loop data
					$loop_order = false;
				}

			}
			if ($loop_order!=false) {
				foreach($loop_order as $pkgname) {
					$build_order[] = $pkgname;
				}
			
				// Adjust $in_queue variable
				foreach($loop as $loop_item => $loop_item_deps) {
					if (inQueue($loop_item, $loop_order)) $in_queue--;
				}
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
	if (!getenv('NO_MERGE_MULTIPKG') || getenv('NO_MERGE_MULTIPKG')!=='YES') $deps = mergeMultiPackages($deps);
	$build_order = resolve($deps);
	return $build_order;

}

function run($argc, $argv) {
	$package_set = read_cmdline($argc, $argv);
	$build_order = getBuildOrder($package_set);


	printArray($build_order);


}


//run($argc, $argv);
