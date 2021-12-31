import json

with open('../setting.json', 'r') as setting:
    setting_dict = json.load(setting)

# Google service account key
KEYPATH          = setting_dict.get('KEYPATH', None)

# BigQuery dataset structure
DATA_CENTER_NAME = setting_dict.get('DATA_CENTER_NAME', None)
TABLE_NAME       = setting_dict.get('TABLE_NAME', None)

# datalab user info(네이버 데이터랩 API 사용자 정보)
CLIENT_LIST      = [(client['CLIENT_ID'], client['CLIENT_SECRET']) for client in setting_dict.get('DATALAB_INFO', None)]

# searchad user info(네이버 검색광고 API 사용자 정보)
CUSTOMER_LIST    = [(customer['CUSTOMER_ID'], customer['SECRET_KEY'], customer['ACCESS_LICENCE']) for customer in setting_dict.get('SEARCHAD_INFO', None)]