AgiliaLinux autobuild system
============================

This scripts should build AgiliaLinux abuilds in right order. The project goal is an ability to build complete distro with one command.

Requirements
------------
This is a proof-of-concept version, so languages used are not the ones which would be used in final version. At this time, dependencies are:
* php 5.3
* bash
* wget

Also, this script assumes that your abuild tree is placed at $HOME/abuilds. If not, edit config.php to change path.

Usage
-----

./buildorder.php PACKAGE_NAME

