#!/bin/sh

SHELLHOME=$( dirname "$0" )

cd "$SHELLHOME"

if [ -f "venv/bin/activate" ]; then
  . venv/bin/activate
  PYTHON=python
else
  echo "venv: not found, using system-wide python"
  echo "please install python2.7 to ./venv"
  PYTHON=python2.7
fi;

export FLASK_ENV=development
$PYTHON server.py -p 8888 --rendering xslt --kps 150
