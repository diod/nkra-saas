#!/bin/sh

SHELLHOME=$( dirname "$0" )

cd "$SHELLHOME"

if [ -f "venv/bin/activate" ]; then
  . venv/bin/activate
  OPTS="-H venv"
else
  echo "venv: not found, using system-wide uwsgi, python and packages"
  echo "please install with ./venv.sh"
fi;

UWSGI=$( which uwsgi )
if [ "$?" -ne 0 ]; then
  echo "uwsgi not found, please check your venv match requirements.txt"
  exit 1
fi;

exec uwsgi $OPTS --yml saas.yml
