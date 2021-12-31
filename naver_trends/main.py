#! python
import os
from constant import IS_DANGEROUS_TIME
from uinfo import *
from keywordanal import Keywordanal
from google.cloud import bigquery
import pandas as pd
import queries

if __name__ == '__main__':
    # check if it is dangerous time
    if (IS_DANGEROUS_TIME):
        print('Deny access to the server. It is a dangerous time.')
        exit()

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = KEYPATH
    client_list = os.listdir('../data')

    # keyword analysis tool
    keyword_anal = Keywordanal()

    # BigQuery client
    bq = bigquery.Client()

    for client in client_list:
        brand_id = client.split('_')[-1]

        # read keywords file
        with open(f'../data/{client}/keywords.txt', 'r', encoding='utf-8') as keyword_file:
            keyword_list = keyword_file.read().upper().replace(' ', '').strip().split('\n')
        
        # divide into 5 keywords
        keyword_list = [keyword_list[i:i+5] for i in range(0, len(keyword_list), 5)]

        # get table infomation
        table = bq.get_table(f'{DATA_CENTER_NAME}.{client}.{TABLE_NAME}')
        selected_fields = [
            bigquery.SchemaField('device_type', 'STRING'),
            bigquery.SchemaField('brand_id', 'STRING'),
            bigquery.SchemaField('queries', 'INTEGER'),
            bigquery.SchemaField('keyword', 'STRING'),
            bigquery.SchemaField('date', 'STRING')
        ]

        # find latest date
        q = queries.find_latest_date.format(DATA_CENTER_NAME, client, TABLE_NAME)
        q_result = bq.query(q).result()
        i_result = None

        # update table
        if (q_result.total_rows != 0):
            latest_date_dict = {}
            
            for row in q_result:
                if row.device_type not in latest_date_dict:
                    latest_date_dict[row.device_type] = {}
                latest_date_dict[row.device_type][row.keyword] = row.latest_date

            df = pd.DataFrame(columns=['device_type', 'brand_id', 'queries', 'keyword', 'date'])
            for chunk in keyword_list:
                print("processing : ", chunk)
                keyword_dict = keyword_anal.list_to_dict(chunk, latest_date_dict)

                for keyword in chunk:
                    pc_data = {
                        'device_type': 'pc',
                        'brand_id': brand_id,
                        'queries': keyword_dict[keyword]['dpc'].values(),
                        'keyword': keyword,
                        'date': keyword_dict[keyword]['dpc'].keys()
                    }
                    mo_data = {
                        'device_type': 'mo',
                        'brand_id': brand_id,
                        'queries': keyword_dict[keyword]['dmc'].values(),
                        'keyword': keyword,
                        'date': keyword_dict[keyword]['dmc'].keys()
                    }
                    df = pd.concat([df, pd.DataFrame(pc_data), pd.DataFrame(mo_data)])
            i_result = bq.insert_rows_from_dataframe(table=table, dataframe=df, selected_fields=selected_fields)

        else:
            for chunk in keyword_list:
                print("processing : ", chunk)
                keyword_dict = keyword_anal.list_to_dict(chunk)
                df = pd.DataFrame(columns=['device_type', 'brand_id', 'queries', 'keyword', 'date'])

                for keyword in chunk:
                    pc_data = {
                        'device_type': 'pc',
                        'brand_id': brand_id,
                        'queries': keyword_dict[keyword]['dpc'].values(),
                        'keyword': keyword,
                        'date': keyword_dict[keyword]['dpc'].keys()
                    }
                    mo_data = {
                        'device_type': 'mo',
                        'brand_id': brand_id,
                        'queries': keyword_dict[keyword]['dmc'].values(),
                        'keyword': keyword,
                        'date': keyword_dict[keyword]['dmc'].keys()
                    }
                    df = pd.concat([df, pd.DataFrame(pc_data), pd.DataFrame(mo_data)])
                i_result = bq.insert_rows_from_dataframe(table=table, dataframe=df, selected_fields=selected_fields)

        if (type(i_result) == list):
            print('{} Done'.format(client))
        else:
            print('{} Failed'.format(client))