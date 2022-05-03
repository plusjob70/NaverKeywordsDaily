import json

with open('../setting.json', 'r') as setting:
    setting_dict = json.load(setting)

# Google service account key
KEYPATH = setting_dict.get('KEYPATH', None)
OAUTHPATH = setting_dict.get('OAUTHPATH', None)
TOKENPATH = setting_dict.get('TOKENPATH', None)

# BigQuery dataset structure
PROJECT_NAME = setting_dict.get('PROJECT_NAME', None)
BASIC_TABLE_NAME = setting_dict.get('BASIC_TABLE_NAME', None)
GENDER_TABLE_NAME = setting_dict.get("GENDER_TABLE_NAME", None)

# Gmail service
SENDER_EMAIL = setting_dict.get('SENDER_EMAIL', None)
RECEIVER_EMAIL_LIST = [email for email in setting_dict.get('RECEIVER_EMAIL', None)]

# Google Drive directory name
GDRIVE_DIR_NAME = setting_dict.get('GDRIVE_DIR_NAME', None)

# datalab user info(네이버 데이터랩 API 사용자 정보)
CLIENT_LIST = [(client['CLIENT_ID'], client['CLIENT_SECRET']) for client in setting_dict.get('DATALAB_INFO', None)]

# searchad user info(네이버 검색광고 API 사용자 정보)
CUSTOMER_LIST = [
    (customer['CUSTOMER_ID'], customer['SECRET_KEY'], customer['ACCESS_LICENCE'], customer['UID'], customer['UPW'])
    for customer in setting_dict.get('SEARCHAD_INFO', None)
]

# check validation
assert KEYPATH, 'Insert KEYPATH in setting.json file'
assert OAUTHPATH, 'Insert OAUTHPATH in setting.json file'
assert TOKENPATH, 'Insert TOKENPATH in setting.json file'
assert PROJECT_NAME, 'Insert PROJECT_NAME in setting.json file'
assert BASIC_TABLE_NAME, 'Insert BASIC_TABLE_NAME in setting.json file'
assert GENDER_TABLE_NAME, 'Insert GENDER_TABLE_NAME in setting.json file'
assert SENDER_EMAIL, 'Insert SENDER_EMAIL in setting.json file'
assert RECEIVER_EMAIL_LIST, 'Insert RECEIVER_EMAIL_LIST in setting.json file'
assert GDRIVE_DIR_NAME, 'Insert GDRIVE_DIR_NAME in setting.json file'
assert CLIENT_LIST, 'Insert CLIENT_LIST in setting.json file'
assert CUSTOMER_LIST, 'Insert CUSTOMER_LIST in setting.json file'
