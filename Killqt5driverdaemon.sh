#!/bin/bash

thisdir=$(dirname "$0")
cd $thisdir
daemon_pid=`pgrep -f "Qt5DriverDaemon"`
kill $daemon_pid &
