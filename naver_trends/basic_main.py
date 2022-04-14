#! /usr/bin/env python

def main():
    import sys
    import pandas as pd
    from naver_trends.common.constant \
        import IS_DANGEROUS_TIME, MAX_ANAL_BATCH_SIZE, MIN_INSERT_BATCH_SIZE, BIGQUERY_CHUNK_SIZE
    from naver_trends.keywordanal.keywordanal import Keywordanal
    from naver_trends.service.bigqueryservice import BigQueryService
    from naver_trends.service.gsheetsservice import GSheetsService
    from naver_trends.service.gmailservice import GmailService

    # check dangerous time
    if IS_DANGEROUS_TIME:
        sys.exit('Deny access to the server. It is a dangerous time.')

    MODE = 'basic'

    # extract selected_client_list
    selected_client_name_list = sys.argv[1:]

    # BigQuery table schema
    schema = {
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
        'device_type': 'STRING'
    }

    # create BigQueryService & GSheetsService & GmailService & keyword analyze tool & DataFrame instance
    bigquery = BigQueryService(schema=schema, mode=MODE)
    gsheets = GSheetsService()
    gmail = GmailService()
    keyword_anal = Keywordanal()
    dataframe_cols = schema.keys()

    print(gmail.write_message(f'mode : {MODE}'), flush=True)

    # get all client's information
    # client_info_list = list[dict{id, name}, dict{id, name}, ...]
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
        keyword_anal.latest_date_dict = bigquery.get_latest_date_dict(client_name=client_name)

        for point in range(0, sheet_size, MAX_ANAL_BATCH_SIZE):
            sheet_chunk_list = sheet[point:point + MAX_ANAL_BATCH_SIZE]
            keyword_list = list(map(lambda chunk: chunk['keyword'], sheet_chunk_list))
            print(keyword_list, flush=True)

            keyword_dict = keyword_anal.get_results(keyword_list=keyword_list)

            for idx, row in enumerate(sheet_chunk_list):
                pc_data_size = len(keyword_dict[keyword_list[idx]]['dpc'])
                if pc_data_size > 0:
                    row['date'] = keyword_dict[keyword_list[idx]]['dpc'].keys()
                    row['queries'] = keyword_dict[keyword_list[idx]]['dpc'].values()
                    row['device_type'] = 'PC'
                    dataframe_list.append(pd.DataFrame(columns=dataframe_cols, data=sheet_chunk_list[idx]))

                mo_data_size = len(keyword_dict[keyword_list[idx]]['dmc'])
                if mo_data_size > 0:
                    row['date'] = keyword_dict[keyword_list[idx]]['dmc'].keys()
                    row['queries'] = keyword_dict[keyword_list[idx]]['dmc'].values()
                    row['device_type'] = '모바일'
                    dataframe_list.append(pd.DataFrame(columns=dataframe_cols, data=sheet_chunk_list[idx]))
                dataframe_rows = dataframe_rows + pc_data_size + mo_data_size

            if dataframe_rows > MIN_INSERT_BATCH_SIZE:
                insert_results = bigquery.client.insert_rows_from_dataframe(
                    table=table,
                    dataframe=pd.concat(dataframe_list),
                    selected_fields=bigquery.table_schema,
                    chunk_size=BIGQUERY_CHUNK_SIZE
                )
                dataframe_rows = 0
                dataframe_list = []
                if sum(map(lambda x: len(x), insert_results)):
                    print(insert_results)
                    print(gmail.write_message("----insertion failed----"), flush=True)
                    gmail.tag = 'failed'
                else:
                    print("----insertion successful----", flush=True)

        if dataframe_rows:
            insert_results = bigquery.client.insert_rows_from_dataframe(
                table=table,
                dataframe=pd.concat(dataframe_list),
                selected_fields=bigquery.table_schema,
                chunk_size=BIGQUERY_CHUNK_SIZE
            )

        if sum(map(lambda x: len(x), insert_results)):
            print(gmail.write_message(f'{client_name} failed.'), flush=True)
            gmail.tag = 'failed'
        else:
            print(gmail.write_message(f'{client_name} Done.'), flush=True)

    gmail.send_message()


if __name__ == '__main__':
    main()
