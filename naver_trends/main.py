#! /usr/bin/env python

import sys
import pandas as pd
from naver_trends.common.constant \
    import IS_DANGEROUS_TIME, MAX_ANAL_BATCH_SIZE, MIN_INSERT_BATCH_SIZE, BIGQUERY_CHUNK_SIZE
from naver_trends.keywordanal import *
from naver_trends.service.bigqueryservice import BigQueryService
from naver_trends.service.gsheetsservice import GSheetsService
from naver_trends.service.gmailservice import GmailService


class NaverKeywordsTool:
    def __init__(self, _mode='device'):
        # BigQuery table schema
        self.schema = {
            'corporate_id': 'STRING',
            'brand_id': 'STRING',
            'keyword': 'STRING',
            'keyword_type': 'STRING',
            'category_1': 'STRING',
            'category_2': 'STRING',
            'category_3': 'STRING',
            'category_4': 'STRING',
            'category_5': 'STRING',
            'date': 'STRING',
            'queries': 'INTEGER',
        }

        # Analyzer mode
        self.mode = _mode
        self.add_col = None
        self.analyzer = None
        self.labels = None

        if self.mode == 'device':
            self.add_col = 'device_type'
            self.analyzer = device_analyzer.DeviceAnalyzer()
            self.labels = [('PC', 'dpc'), ('모바일', 'dmc')]
        elif self.mode == 'gender':
            self.add_col = 'gender_type'
            self.analyzer = gender_analyzer.GenderAnalyzer()
            self.labels = [('남', 'dmc'), ('여', 'dfc')]
        elif self.mode == 'age':
            self.add_col = 'age_group'
            self.analyzer = age_analyzer.AgeAnalyzer()
            self.labels = [
                ('0-12', 'd0c'), ('13-19', 'd13c'), ('20-24', 'd20c'),
                ('25-29', 'd25c'), ('30-39', 'd30c'), ('40-49', 'd40c'), ('50-', 'd50c')
            ]
        else:
            sys.exit('None type')

        self.schema[self.add_col] = 'STRING'

    def execute(self, selected_client_name_list):
        bigquery = BigQueryService(schema=self.schema, mode=self.mode)
        gsheets = GSheetsService()
        gmail = GmailService()
        dataframe_cols = self.schema.keys()

        try:
            print(gmail.write_message(f'mode : {self.mode}'), flush=True)

            """
            get all client's information
            client_info_list = list[dict{id, name}, dict{id, name}, ...]
            """
            client_info_list = gsheets.get_all_files_info()

            print('Start to analyze keywords...', flush=True)
            for client in client_info_list:
                client_id = client['id']
                client_name = client['name']

                if (client_name not in selected_client_name_list) and selected_client_name_list:
                    continue

                print(gmail.write_message(f'Analyzing keywords for client : {client_name}'), flush=True)

                if not bigquery.is_exist_dataset(client_name=client_name):
                    print(gmail.write_message(f'\"{client_name}\" dataset is not exist'), flush=True)
                    continue

                dataframe_rows = 0
                dataframe_list = []
                insert_results = []

                # get sheet file
                sheet = gsheets.get_sheet(_id=client_id)
                sheet_size = len(sheet)

                # preprocess sheet data
                for idx in range(sheet_size):
                    sheet[idx]['keyword'] = sheet[idx]['keyword'].replace(' ', '').upper()

                # get table information
                table = bigquery.get_table_info(client_name=client_name)

                # set the latest date
                self.analyzer.set_latest_date_dict(bigquery.get_latest_date_dict(client_name=client_name))

                for point in range(0, sheet_size, MAX_ANAL_BATCH_SIZE):
                    sheet_chunk_list = sheet[point:point + MAX_ANAL_BATCH_SIZE]
                    keyword_list = list(map(lambda chunk: chunk['keyword'], sheet_chunk_list))
                    print(keyword_list, flush=True)

                    keyword_dict = self.analyzer.get_results(keyword_list=keyword_list)

                    for idx, row in enumerate(sheet_chunk_list):
                        for category, daily_clicks in self.labels:
                            data_size = len(keyword_dict[keyword_list[idx]][daily_clicks])
                            if data_size > 0:
                                row['date'] = keyword_dict[keyword_list[idx]][daily_clicks].keys()
                                row['queries'] = keyword_dict[keyword_list[idx]][daily_clicks].values()
                                row[self.add_col] = category
                                dataframe_list.append(pd.DataFrame(columns=dataframe_cols, data=sheet_chunk_list[idx]))
                            dataframe_rows += data_size

                    if dataframe_rows > MIN_INSERT_BATCH_SIZE:
                        insert_results = bigquery.client.insert_rows_from_dataframe(
                            table=table,
                            dataframe=pd.concat(dataframe_list),
                            selected_fields=bigquery.table_schema,
                            chunk_size=BIGQUERY_CHUNK_SIZE
                        )
                        if any(insert_results):
                            print(insert_results)
                            print(gmail.write_message("----insertion failed----"), flush=True)
                            gmail.tag = 'failed'
                        else:
                            print("----insertion successful----", flush=True)
                        dataframe_rows = 0
                        dataframe_list = []

                if dataframe_rows:
                    insert_results = bigquery.client.insert_rows_from_dataframe(
                        table=table,
                        dataframe=pd.concat(dataframe_list),
                        selected_fields=bigquery.table_schema,
                        chunk_size=BIGQUERY_CHUNK_SIZE
                    )
                    if any(insert_results):
                        print(insert_results)
                        print(gmail.write_message(f'{client_name} failed.'), flush=True)
                        gmail.tag = 'failed'
                    else:
                        print(gmail.write_message(f'{client_name} Done.'), flush=True)

        except Exception as e:
            gmail.tag = 'failed'
            print(gmail.write_message(str(e)))

        finally:
            gmail.send_message()


if __name__ == '__main__':
    # check dangerous time
    if IS_DANGEROUS_TIME:
        sys.exit('Deny access to the server. It is a dangerous time.')

    if (_mode := sys.argv[1]) not in ['device', 'gender', 'age']:
        sys.exit('Select device or gender or age mode.')

    nkt = NaverKeywordsTool(_mode)
    nkt.execute(sys.argv[2:])
