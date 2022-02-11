case "$OSTYPE" in
  darwin*)  dir="bin" ;; 
  linux*)   dir="bin" ;;
  msys*)    dir="Scripts" ;;
  cygwin*)  dir="Scripts" ;;
  *)        dir="None" ;;
esac

if [ -d "env" ]; then
    source env/naver_trends_venv/${dir}/activate
else
    mkdir env
    cd env && python -m venv "naver_trends_venv" && cd ..

    source env/naver_trends_venv/${dir}/activate
    
    pip install --upgrade requests
    pip install --upgrade pandas
    pip install --upgrade google-cloud-bigquery
    pip install --upgrade gspread
    pip install --upgrade oauth2client
    pip install --upgrade google-api-python-client
fi

python basic_main.py

exec $SHELL