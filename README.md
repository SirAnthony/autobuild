AgiliaLinux autobuild system
============================

This scripts should build AgiliaLinux abuilds in right order. The project goal is an ability to build complete distro with one command.

Requirements
------------
This is a proof-of-concept version, so languages used are not the ones which would be used in final version. At this time, dependencies are:
* php 5.3
* bash
* wget
* graphviz (optional, for dependency graph visualization)
* some image viewer (optional, for displaying dependency graphs)

Also, this script assumes that your abuild tree is placed at $HOME/abuilds. If not, edit config.php to change path.

Usage
-----
Some useful things are there, and you can try it. General usage: ./script.php pkg1 pkg2 pkg3

What do we have:
* graph.php - generates dependency graph between specified packages and related ones. Generates depgraph.dot file, renders depgraph.dot.png and displays it if possible
* build.php - decides what to do if we want to build specified packages. Later, it will be extended to actually do these things.
* print_buildorder.php - prints build order for specified packages. Mostly for debugging.

