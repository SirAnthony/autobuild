#!/bin/bash
AUTOBUILD_LOG=${HOME}autobuild.log DO_BUILD=YES ./build.py $(cat minimal-build.list)
