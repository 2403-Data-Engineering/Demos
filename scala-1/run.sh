#!/usr/bin/env bash
# This will compile all scala files in the directory, then execute based on which object was given

if [ -z "$1" ]; then
  echo "Usage: ./run.sh <ObjectName>"
  exit 1
fi

mkdir -p target
scalac -d target *.scala && scala -cp target "$1"