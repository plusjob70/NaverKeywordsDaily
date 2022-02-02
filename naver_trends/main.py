#! python
import pandas as pd
from time import sleep
from naver_trends.common.constant import IS_DANGEROUS_TIME
from naver_trends.keywordanal.keywordanal import Keywordanal
from naver_trends.service.gmailservice import GmailService
from naver_trends.service.bigqueryservice import BigQueryService
from naver_trends.service.gsheetsservice import GSheetsService
from google.cloud.exceptions import NotFound


if __name__ == '__main__':
    msg    = []
    text   = ''
    status = 'succeeded'

    # create GmailService instance
    #gmail  = GmailService()

    # check dangerous time
    if (IS_DANGEROUS_TIME):
        text = 'Deny access to the server. It is a dangerous time.'
        print(text)
        #gmail.send_message(gmail.create_message(text, 'failed'))
        exit()

    # BigQuery table schema
    schema = {
        'corporate_id': 'STRING',
        'brand_id'    : 'STRING',
        'date'        : 'STRING',
        'keyword'     : 'STRING',
        'keyword_type': 'STRING',
        'category_1'  : 'STRING',
        'category_2'  : 'STRING',
        'category_3'  : 'STRING',
        'category_4'  : 'STRING',
        'category_5'  : 'STRING',
        'device_type' : 'STRING',
        'queries'     : 'INTEGER'
    }
    # dataframe columns
    df_columns   = schema.keys()

    # create BigQueryService & GSheetsService & keyword anal tool instance
    bigquery     = BigQueryService(schema=schema)
    gsheets      = GSheetsService()
    keyword_anal = Keywordanal()

    # get client file info (id, name)
    client_info_dict = gsheets.get_all_files_info()

    print('Start to analyze keywords...', flush=True)
    for client in client_info_dict:
        client_id   = client['id']
        client_name = client['name']
        text        = 'Analyzing keywords for client : {}'.format(client_name)
        msg.append(text)
        print(text, flush=True)

        # get sheet file
        sheet = gsheets.get_sheet(id=client_id)

        # preprocess sheet data
        for idx in range(len(sheet)):
            sheet[idx]['keyword'] = sheet[idx]['keyword'].replace(' ', '').upper()
        sheet_data_list = [sheet[i:i+5] for i in range(0, len(sheet), 5)]
        
        # get table infomation
        table = bigquery.get_table_info(client_name)

        # find latest date
        num_rows, s_result = bigquery.get_latest_date_dict(client_name)

        # update table
        i_result = None
        if (num_rows != 0):
            latest_date_dict = {}
            for row in s_result:
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
                    mo_data = {
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
                text = '"{}" No change in data'.format(client_name) 
                print(text, flush=True)
                msg.append(text)
                continue
            else:
                print(df, flush=True)
                print('Inserting to BigQuery table...', flush=True)
                i_result = bigquery.client.insert_rows_from_dataframe(table=table, dataframe=df, selected_fields=bigquery.table_schema)

        else:
            print('New table found.', flush=True)
            time_out = 0
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
                    mo_data = {
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

                while (True):
                    try:
                        i_result = bigquery.client.insert_rows_from_dataframe(table=table, dataframe=df, selected_fields=bigquery.table_schema)
                        break
                    except NotFound:
                        print('not found table because of delay. please wait...', flush=True)
                        time_out += 1
                        sleep(0.5)
                        if (time_out > 50):
                            text = '"{}" BigQuery table not found'.format(client_name)
                            print(text, flush=True)
                            #gmail.send_message(gmail.create_message(text, 'failed'))
                            exit()
                        continue

        if (type(i_result) is list):
            text = '{} Done'.format(client_name)
        else:
            text = '{} Failed'.format(client_name)
            status = 'failed'
        print(text, flush = True)
        msg.append(text)

    msg ='\n'.join(msg)
    #gmail.send_message(gmail.create_message(msg, status))