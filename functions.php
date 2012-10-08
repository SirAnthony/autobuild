<?php
function debug($msg) {
	//echo $msg . "\n";
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
	system("dot -Tpng -O $fname.dot 2>/dev/null");
	return $data;
}


function isBlacklist($p) {
	$blacklist = array("aaa_elflibs", "aaa_base", "aaa_terminfo", "aaa_elflibs_dummy");
	foreach($blacklist as $b) {
		if ($b == $p) return true;
	}
	return false;
}

function inQueue($pkgname, $array) {
	foreach($array as $a) {
		if ($a===$pkgname) return true;
	}
	return false;
}

function get_builddeps($abuild) {
	debug("GET: $abuild");
	if (!file_exists($abuild)) {
		debug("GET_ERROR: No such file $abuild");
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
	return $ret;
}

function printArray($array) {
	foreach($array as $b) {
		echo $b . "\n";
	}

}
