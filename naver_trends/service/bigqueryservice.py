import os
import naver_trends.common.queries as queries
from time import sleep
from naver_trends.common.uinfo import GENDER_TABLE_NAME, KEYPATH, PROJECT_NAME, BASIC_TABLE_NAME
from google.cloud.bigquery import Client
from google.cloud.bigquery.schema import SchemaField
from google.cloud.bigquery.table import Table
from google.cloud.exceptions import NotFound


class BigQueryService:
    # schema : dict = {'column name' : 'bigquery type'}
    def __init__(self, schema: dict = None, mode: str = 'basic'):
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = KEYPATH
        self.client = Client(project=PROJECT_NAME)
        self.table_schema = None
        self.table_name = None
        self.mode = mode
        self.sep = None

        if schema is not None:
            self.table_schema = [SchemaField(col, type) for col, type in schema.items()]

        if self.mode == 'basic':
            self.table_name = BASIC_TABLE_NAME
            self.sep = 'device_type'
        elif self.mode == 'gender':
            self.table_name = GENDER_TABLE_NAME
            self.sep = 'gender'

    # check dataset existence
    def is_exist_dataset(self, client_name: str):
        try:
            self.client.get_dataset(client_name)
            return True
        except NotFound:
            return False

    # if table exists then get information of table
    # else create table then get information of table
    def get_table_info(self, client_name: str):
        table = None
        table_id: str = f'{PROJECT_NAME}.{client_name}.{self.table_name}'
        try:
            table = self.client.get_table(table_id)
        except NotFound:
            print('Creating table...', flush=True)
            table = self.client.create_table(Table(table_ref=table_id, schema=self.table_schema))

            chance = 60
            while chance > 0:
                try:
                    table = self.client.get_table(table_id)
                    print('table is created')
                    break
                except NotFound:
                    chance -= 1
                    print(f'not found table because of delay. please wait... {chance}', flush=True)
                    sleep(0.5)
        return table

    # get latest date
    def get_latest_date_dict(self, client_name: str):
        latest_date_dict = {}

        result = self.client.query(
            queries.find_latest_date.format(sep=self.sep, project=PROJECT_NAME,
                                            dataset=client_name, table=self.table_name)
        ).result()

        if result.total_rows > 0:
            for row in result:
                sep = row.gender if (self.mode == 'gender') else row.device_type
                if sep not in latest_date_dict:
                    latest_date_dict[sep] = {}
                latest_date_dict[sep][row.keyword] = row.latest_date
        return latest_date_dict

    def get_dataset_list(self):
        return [dataset.dataset_id for dataset in list(self.client.list_datasets())]
