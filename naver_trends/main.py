#! python
import os
import gspread
import pandas as pd
import common.queries as queries
from common.constant import IS_DANGEROUS_TIME
from common.uinfo import *
from keywordanal import Keywordanal
from google.cloud import bigquery
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

if __name__ == '__main__':
    # check dangerous time
    if (IS_DANGEROUS_TIME):
        print('Deny access to the server. It is a dangerous time.')
        exit()

    # set google application credentials for Bigquery
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = KEYPATH

    # authorize gsheet and gdrive
    scope  = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    creds  = ServiceAccountCredentials.from_json_keyfile_name(KEYPATH, scope)
    gdrive = build('drive', 'v3', credentials=creds)
    gspd   = gspread.authorize(credentials=creds)

    # get client file info (id, name)
    nst_data_id      = gdrive.files().list(q=f'name=\'{GDRIVE_DIR_NAME}\'').execute().get('files')[0].get('id')
    client_info_dict = gdrive.files().list(q=f'\'{nst_data_id}\' in parents', fields='files(id, name)', pageSize=1000).execute().get('files')

    # keyword analysis tool
    keyword_anal = Keywordanal()

    # BigQuery client
    bq = bigquery.Client()

    # dataframe columns
    df_columns = [
        'corporate_id', 'brand_id', 'date', 'keyword', 'keyword_type', 'category_1',
        'category_2', 'category_3', 'category_4', 'category_5', 'device_type', 'queries'
    ]

    # BigQuery table columns
    selected_fields = [
        bigquery.SchemaField('corporate_id', 'STRING'),
        bigquery.SchemaField('brand_id', 'STRING'),
        bigquery.SchemaField('date', 'STRING'),
        bigquery.SchemaField('keyword', 'STRING'),
        bigquery.SchemaField('keyword_type', 'STRING'),
        bigquery.SchemaField('category_1', 'STRING'),
        bigquery.SchemaField('category_2', 'STRING'),
        bigquery.SchemaField('category_3', 'STRING'),
        bigquery.SchemaField('category_4', 'STRING'),
        bigquery.SchemaField('category_5', 'STRING'),
        bigquery.SchemaField('device_type', 'STRING'),
        bigquery.SchemaField('queries', 'INTEGER')
    ]

    print('Start to analyze keywords...', flush=True)
    for client in client_info_dict:
        client_id   = client['id']
        client_name = client['name']
        print('Analyzing keywords for client:', client_name, flush=True)

        # get sheet file
        sheet = gspd.open_by_key(client_id).sheet1.get_all_records()

        # preprocess sheet data
        for idx in range(len(sheet)):
            sheet[idx]['keyword'] = sheet[idx]['keyword'].replace(' ', '').upper()
        sheet_data_list = [sheet[i:i+5] for i in range(0, len(sheet), 5)]
        
        # get table infomation
        table = bq.get_table(f'{PROJECT_NAME}.{client_name}.{TABLE_NAME}')

        # find latest date
        q = queries.find_latest_date.format(PROJECT_NAME, client_name, TABLE_NAME)
        q_result = bq.query(q).result()
        i_result = None

        # update table
        if (q_result.total_rows != 0):
            latest_date_dict = {}
            for row in q_result:
                if row.device_type not in latest_date_dict:
                    latest_date_dict[row.device_type] = {}
                latest_date_dict[row.device_type][row.keyword] = row.latest_date

            keyword_anal.set_latest_date_dict(latest_date_dict)

            df = pd.DataFrame(columns=df_columns)
            for chunk in sheet_data_list:
                keyword_list = [row.get('keyword', None) for row in chunk]
                keyword_dict = keyword_anal.get_keyword_anal_results(keyword_list)
                print(keyword_list, flush=True)

                for idx, row in enumerate(chunk):
                    pc_data = {
                        'corporate_id': row['corporate_id'],
                        'brand_id'    : row['brand_id'],
                        'date'        : keyword_dict[keyword_list[idx]]['dpc'].keys(),
                        'keyword'     : row['keyword'],
                        'keyword_type': row['keyword_type'],
                        'category_1'  : row['category_1'],
                        'category_2'  : row['category_2'],
                        'category_3'  : row['category_3'],
                        'category_4'  : row['category_4'],
                        'category_5'  : row['category_5'],
                        'device_type' : 'PC',
                        'queries'     : keyword_dict[keyword_list[idx]]['dpc'].values()
                    }
                    mo_data ={
                        'corporate_id': row['corporate_id'],
                        'brand_id'    : row['brand_id'],
                        'date'        : keyword_dict[keyword_list[idx]]['dmc'].keys(),
                        'keyword'     : row['keyword'],
                        'keyword_type': row['keyword_type'],
                        'category_1'  : row['category_1'],
                        'category_2'  : row['category_2'],
                        'category_3'  : row['category_3'],
                        'category_4'  : row['category_4'],
                        'category_5'  : row['category_5'],
                        'device_type' : '모바일',
                        'queries'     : keyword_dict[keyword_list[idx]]['dmc'].values()
                    }
                    df = pd.concat([df, pd.DataFrame(pc_data), pd.DataFrame(mo_data)])

            if (df.empty):
                print('"{}" No change in data'.format(client_name), flush=True)
                continue
            else:
                print(df, flush=True)
                print('Inserting to BigQuery table...', flush=True)
                i_result = bq.insert_rows_from_dataframe(table=table, dataframe=df, selected_fields=selected_fields)

        else:
            print('New table found.', flush=True)
            keyword_anal.set_latest_date_dict(latest_date_dict={})

            for chunk in sheet_data_list:
                keyword_list = [row.get('keyword', None) for row in chunk]
                keyword_dict = keyword_anal.get_keyword_anal_results(keyword_list)
                print(keyword_list, flush=True)

                df = pd.DataFrame(columns=df_columns)
                for idx, row in enumerate(chunk):
                    pc_data = {
                        'corporate_id': row['corporate_id'],
                        'brand_id'    : row['brand_id'],
                        'date'        : keyword_dict[keyword_list[idx]]['dpc'].keys(),
                        'keyword'     : row['keyword'],
                        'keyword_type': row['keyword_type'],
                        'category_1'  : row['category_1'],
                        'category_2'  : row['category_2'],
                        'category_3'  : row['category_3'],
                        'category_4'  : row['category_4'],
                        'category_5'  : row['category_5'],
                        'device_type' : 'PC',
                        'queries'     : keyword_dict[keyword_list[idx]]['dpc'].values()
                    }
                    mo_data ={
                        'corporate_id': row['corporate_id'],
                        'brand_id'    : row['brand_id'],
                        'date'        : keyword_dict[keyword_list[idx]]['dmc'].keys(),
                        'keyword'     : row['keyword'],
                        'keyword_type': row['keyword_type'],
                        'category_1'  : row['category_1'],
                        'category_2'  : row['category_2'],
                        'category_3'  : row['category_3'],
                        'category_4'  : row['category_4'],
                        'category_5'  : row['category_5'],
                        'device_type' : '모바일',
                        'queries'     : keyword_dict[keyword_list[idx]]['dmc'].values()
                    }
                    df = pd.concat([df, pd.DataFrame(pc_data), pd.DataFrame(mo_data)])
                print('Inserting to BigQuery table...', flush=True)
                i_result = bq.insert_rows_from_dataframe(table=table, dataframe=df, selected_fields=selected_fields)

        if (type(i_result) is list):
            print('{} Done'.format(client_name), flush=True)
        else:
            print('{} Failed'.format(client_name), flush=True)