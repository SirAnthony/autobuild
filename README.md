AgiliaLinux autobuild system
============================

This scripts should build AgiliaLinux abuilds in right order. The project goal is an ability to build complete distro with one command.

Requirements
------------
Current status is beta. Dependencies are:
* python
* bash
* wget
* graphviz (optional, for dependency graph visualization)

Also, this script assumes that your abuild tree is placed at $HOME/abuilds. If not, edit config.php to change path.

Usage
-----
Some useful things are there, and you can try it. General usage: ./agibuild.py pkg1 pkg2 pkg3
Run without arguments to obtain options list

Examples:
* `./agibuild.py -g filename <packages_list>`

Generates dependency graph between specified packages and related ones. Generates filename.dot file, renders filename.dot.png and displays it if possible
* `./agibuild.py -o <packages_list>`

Prints build order for specified packages. Mostly for debugging.
* `./agibuild.py -t build_source <packages_list>`

Build packages list using abuilds at build_source

* `./agibuild.py -pudika build_source <packages_list>`
Typical usage for serious mantainer. Build almost everything: all dependencies and dependand packages for packages in list.

TODO
-----
* Install order (install packages when it requires only if all required packages is avaliable)
* Minimal build (install dependencies only when it required and remove when it not needed)
