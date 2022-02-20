#!/usr/bin/zsh
case "$OSTYPE" in
  darwin*)    dir="bin" ;; 
  linux*)     dir="bin" ;;
  msys*)      dir="Scripts" ;;
  cygwin*)    dir="Scripts" ;;
  *)          dir="bin" ;;
esac

cd ..

if [ -d "venv" ]; then
    . ./venv/${dir}/activate
else
    python3 -m venv "venv" && . ./venv/${dir}/activate
    
    pip3 install --upgrade requests
    pip3 install --upgrade pandas
    pip3 install --upgrade google-cloud-bigquery
    pip3 install --upgrade gspread
    pip3 install --upgrade oauth2client
    pip3 install --upgrade google-api-python-client
    pip3 install --upgrade selenium
    
    ./venv/${dir}/bin/python setup.py develop
fi

cd naver_trends && python3 basic_main.py

exec $SHELL