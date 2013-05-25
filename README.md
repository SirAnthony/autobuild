AgiliaLinux autobuild system
============================

This scripts should build AgiliaLinux abuilds in right order. The project goal is an ability to build complete distro with one command.

Requirements
------------
This is a proof-of-concept version, so languages used are not the ones which would be used in final version. At this time, dependencies are:
* python
* bash
* wget
* graphviz (optional, for dependency graph visualization)
* some image viewer (optional, for displaying dependency graphs)

Also, this script assumes that your abuild tree is placed at $HOME/abuilds. If not, edit config.php to change path.

Usage
-----
Some useful things are there, and you can try it. General usage: ./script.php pkg1 pkg2 pkg3

Examples:
* `./main.py -g filename <packages_list>`

Generates dependency graph between specified packages and related ones. Generates filename.dot file, renders filename.dot.png and displays it if possible
* `./main.py -o <packages_list>`

Prints build order for specified packages. Mostly for debugging.
* `./main.py -t build_source <packages_list>`

Build packages list using abuilds at build_source

