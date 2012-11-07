<?php

// Prints debug messages. You can enable or disable it whenever you want
function debug($msg) {
	if (getenv('DEBUG')) echo $msg . "\n";
}

// Print dependency graph within $loop to $fname
function printGraph($loop, $fname, $highlight = array()) {
	$data = "digraph G {\n";
	foreach($highlight as $pkgname) {
		$data .= "\t\"$pkgname\" [fontcolor = red, color = red];\n";
	}
	foreach($loop as $pkgname => $dep) {
		foreach($dep as $d) {
			$data .= "\t\"$d\" -> \"$pkgname\";\n";
		}
	}
	$data .= "}\n";
	file_put_contents("$fname.dot", $data);
	system("dot -Tpng -O $fname.dot 2>/dev/null");
	return $data;
}

// Checks if specified package is blacklisted from being built or added as dependency. This is a well-known package list and probably will never change.
function isBlacklist($p) {
	$blacklist = array("aaa_elflibs", "aaa_base", "aaa_terminfo", "aaa_elflibs_dummy");
	foreach($blacklist as $b) {
		if ($b == $p) return true;
	}
	return false;
}

// Checks if $pkgname is an $array item
function inQueue($pkgname, $array) {
	foreach($array as $a) {
		if ($a===$pkgname) return true;
	}
	return false;
}

// Parses ABUILD and returns array of build_deps items specified there
function get_builddeps($abuild) {
	debug("GET: $abuild");
	if (!file_exists($abuild)) {
		debug("GET_ERROR: No such file $abuild");
		return array();
	}
	$handle = popen("./get_abuild_var.sh build_deps $abuild", 'r');
	$data = fread($handle, 65536);
	pclose($handle);
	if (trim(preg_replace("/\n/", '', $data))=="") return array();
	$data = preg_replace("/\n/", '', trim($data));
	$deps = explode(' ', $data);
	$ret = array();
	foreach($deps as $d) {
		if (trim($d)!=='' && !isBlacklist($d)) $ret[] = $d;
	}
	return $ret;
}

function getMultipkgSet($pkgname) {
	global $ABUILD_PATH;
	$abuild = $ABUILD_PATH . '/' . $pkgname . '/ABUILD';
	if (!file_exists($abuild)) {
		debug("GET_ERROR: No such file $abuild");
		return array($pkgname);
	}

	$handle = popen("./get_subpackages.sh $abuild", 'r');
	$data = fread($handle, 655360);
	pclose($handle);

	$pkglist = explode("\n", $data);
	$ret = array();
	foreach($pkglist as $p) {
		if (trim($p)==='') continue;
		$ret[] = $p;
	}
	return $ret;
}

function getCorePackage($pkgname) {
	global $ABUILD_PATH;
	$abuild = $ABUILD_PATH . '/' . $pkgname . '/ABUILD';
	if (!file_exists($abuild)) {
		debug("GET_ERROR: No such file $abuild");
		return $pkgname;
	}

	$handle = popen("./get_corepackage.sh $abuild", 'r');
	$data = $pkgname;
	$data = fread($handle, 655360);
	pclose($handle);

	$data = preg_replace("/\n/", '', trim($data));
	if ($data==='') $data = $pkgname;
	return $data;
}
// This function called when build_deps were not specified. This means that package depends only on generic build-essential packages. ATM, this is a hack.
// The code below that was commented out were designed to get package deps from online repository. At this time, we should avoid it.
function get_deps($pkgname) {
	//$ret = array('glibc-solibs', 'gcc');
	$ret = array();
	return $ret;
	/*
	debug("API CALL $pkgname");
	$handle = popen("wget -qO- 'http://api.agilialinux.ru/get_dep.php?n=" . urlencode($pkgname) . "'", 'r');
	$data = fread($handle, 65536);
	debug("RAW API DATA ($pkgname): $data");
	pclose($handle);
	if (trim(preg_replace("/\n/", '', $data))=="") return array();
	$deps = explode("\n", trim($data));
	$ret = array();
	foreach($deps as $d) {
		if (!isBlacklist($d)) $ret[] = $d;
	}
	return $ret;*/
}

// Prints array elements (used for output results)
function printArray($array) {
	$counter = 1;
	foreach($array as $b) {
		if (getenv('NUM')) echo '[' . $counter . '] ';
		echo $b . "\n";
		$counter++;
	}

}

// Filter dupes in array. Removes 2nd and others entries of each dupe items
function filterDupes($array) {
	$ret = array();
	foreach($array as $a) {
		if (!inQueue($a, $ret)) $ret[] = $a;
	}
	return $ret;
}
