#!/bin/bash

SHELLHOME=$( dirname "$0" )

cd "$SHELLHOME"

if [ ! -d "venv" ]; then
  echo "> Setup virtualenv"
  VENV=$( which virtualenv )
  if [ "$?" -ne 0 ]; then
    echo "Could not find virtualenv, please install it using apt/yum/other tool"
    exit 1;
  fi;
  $VENV --python=python2.7 ./venv
  if [ "$?" -ne 0 ]; then
    echo "Virtualenv: failed to setup venv with python2.7"
    exit 1;
  fi;
  
  echo "> Activate venv"
  . ./venv/bin/activate

  echo "> Install requirements"
  pip install -r requirements.txt

  if [ "$?" -ne 0 ]; then
    echo "Whoops, something gone wrong"
    exit 1;
  fi;

  echo  
  echo "Remember to activate virtualenv with"
  echo " . venv/bin/activate"

else
  echo "> Virtualenv already set up, remove ./venv to rebuild"
fi;

exit 0
