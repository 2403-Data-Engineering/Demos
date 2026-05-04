#!/usr/bin/env bash
# This will compile all scala files in the directory, then execute based on which object was given
# ./run.sh Hello
if [ -z "$1" ]; then
  echo "Usage: ./run.sh <ObjectName>"
  exit 1
fi

scalac *.scala && scala "$1"