#!/bin/bash

thisdir=$(dirname "$0")
cd $thisdir
./Qt5Driver.py &
cd $HOME
