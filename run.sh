#!/bin/bash
AUTOBUILD_LOG=/home/aix/autobuild.log DO_BUILD=YES  ./build.php $(cat minimal-build.list)
