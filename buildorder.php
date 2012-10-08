#!/usr/bin/php
<?php

function isBlacklist($p) {
	$blacklist = array("aaa_elflibs", "aaa_base", "aaa_terminfo", "aaa_elflibs_dummy");
	foreach($blacklist as $b) {
		if ($b == $p) return true;
	}
	return false;
}

function get_builddeps($abuild) {
	echo "GET: $abuild\n";
	if (!file_exists($abuild)) {
		echo "GET_ERROR: No such file $abuild\n";
		return array();
	}
	$handle = popen("./get_builddeps.sh $abuild", 'r');
	$data = fread($handle, 65536);
	pclose($handle);
	if (trim(preg_replace("/\n/", '', $data))=="") return array();
	$data = preg_replace("/\n/", '', trim($data));
	$deps = explode(' ', $data);
	$ret = array();
	foreach($deps as $d) {
		if (!isBlacklist($d)) $ret[] = $d;
	}
	return $ret;
}

function get_deps($pkgname) {
	echo "API CALL $pkgname\n";
	$handle = popen("wget -qO- 'http://api.agilialinux.ru/get_dep.php?n=" . urlencode($pkgname) . "'", 'r');
	$data = fread($handle, 65536);
	echo "RAW API DATA ($pkgname): $data\n";
	pclose($handle);
	if (trim(preg_replace("/\n/", '', $data))=="") return array();
	$deps = explode("\n", trim($data));
	$ret = array();
	foreach($deps as $d) {
		if (!isBlacklist($d)) $ret[] = $d;
	}
	return $ret;
}


// Init first line
for($i=1; $i<$argc; $i++) {
	$arg = $argv[$i];
	echo "ARG $arg\n";
	$d = get_builddeps('/home/aix/abuilds/' . $arg . '/ABUILD');
	echo "SIZEOF $arg: " . sizeof($d) . "\n";
	if (sizeof($d)==0) $d = get_deps($arg);
	echo "API_SIZEOF $arg: " . sizeof($d) . "\n";
	$deps[$arg] = $d;
}
$old_size = 0;
$new_size = sizeof($deps);
while ($old_size!=$new_size) {
	echo "WHILE: $old_size != $new_size\n";
	foreach($deps as $pkgname => $pkgdeps) {
		foreach($pkgdeps as $p) {
			if (isset($deps[$p])) continue;
			$d = get_builddeps($p);
			echo "SIZEOF $p: " . sizeof($d) . "\n";
			if (sizeof($d)==0) $d = get_deps($p);
			echo "API_SIZEOF $p: " . sizeof($d) . "\n";
			$deps[$p] = $d;
		}
	}
	$old_size = $new_size;
	$new_size = sizeof($deps);
}
print_r($deps);


// Building build order
$build_order = array();
foreach($deps as $pkgname => $dep ) {
	if (sizeof($dep)==0) {
		echo "ORDER INIT: $pkgname\n";
		$build_order[] = $pkgname;
	}
}

function inQueue($pkgname, $array) {
	foreach($array as $a) {
		if ($a===$pkgname) return true;
	}
	return false;
}

$old_size = 0;
$new_size = sizeof($build_order);
while (sizeof($build_order)<sizeof($deps)) {
	echo "Queue size: " . sizeof($build_order) . "\n";
	foreach($deps as $pkgname => $dep) {
		if (inQueue($pkgname, $build_order)) continue;
		$can_add = true;
		foreach($dep as $d) {
			if (!inQueue($d, $build_order)) {
				echo "CANT ADD $pkgname: $d missing\n";
				$can_add = false;
				break;
			}
		}
		if ($can_add) {
			echo "ORDER ADD: $pkgname\n";
			$build_order[] = $pkgname;
		}
	}

	// Loop detection block
	$old_size = $new_size;
	$new_size = sizeof($build_order);
	if ($old_size===$new_size) {
		$diff = sizeof($deps) - $new_size;
		echo "Loop detected, packages in loop: $diff\n";
		foreach($deps as $pkgname => $dep) {
			if (inQueue($pkgname, $build_order)) continue;
			$loop[$pkgname] = $dep;
		}

		// Read known loop file
		$known_loop = explode(file_get_contents('known_loop'));
		$loop_errors = 0;
		foreach($loop as $l) {
			$found = false;
			foreach($known_loop as $k) {
				if ($l===$k) {
					$found = true;
					break;
				}
			}
			if (!$found) {
				echo "Unknown loop with package $l\n";
				$loop_errors++;
			}
		}
		if ($loop_errors>0) {
			echo "Loop errors detected: $loop_errors, printing loop graph\n";
			echo printGraph($loop, "loop");
			break;
		}
		else {
			// Add loop twice
			for ($i=0; $i<2; $i++) {
				foreach($known_loop as $k) {
					foreach($loop as $l) {
						if ($k===$l) $build_order[] = $l;
					}
				}
			}
		}
	}
}

function printGraph($loop, $fname) {
	$data = "digraph G {\n";
	foreach($loop as $pkgname => $dep) {
		foreach($dep as $d) {
			$data .= "\t\"$pkgname\" -> \"$d\";\n";
		}
	}
	$data .= "}\n";
	file_put_contents("$fname.dot", $data);
	system("dot -Tpng -O $fname.dot");
	return $data;
}
print_r($build_order);
echo printGraph($deps, "deps");
