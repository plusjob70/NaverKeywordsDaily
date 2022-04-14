#!/bin/zsh

BASEDIR=$(dirname "$0")
cd "$BASEDIR"/.. || exit

if [ -d "venv" ]; then
  . ./venv/bin/activate
else
  python3 -m venv "venv" && . ./venv/bin/activate && pip3 install -r requirements.txt
  ./venv/bin/python setup.py develop
fi

cd GUI && python3 nstgui.py

exec "$SHELL"