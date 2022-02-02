import os
import naver_trends.common.queries as queries
from naver_trends.common.uinfo import KEYPATH, PROJECT_NAME, TABLE_NAME
from google.cloud.bigquery import Client
from google.cloud.bigquery.schema import SchemaField
from google.cloud.bigquery.table import Table
from google.cloud.exceptions import NotFound

class BigQueryService():
    # schema : dict = {'column name' : 'bigquery type'}
    def __init__(self, schema: dict = None):
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = KEYPATH
        self.client       = Client(project=PROJECT_NAME)
        self.table_schema = None

        if schema is not None:
            self.table_schema = [SchemaField(col, type) for col, type in schema.items()]

    # if table exists then get infomation of table
    # else create table then get infomation of table
    def get_table_info(self, client_name:str):
        table     = None
        table_id  = f'{PROJECT_NAME}.{client_name}.{TABLE_NAME}'
        try:
            table = self.client.get_table(table_id)
        except NotFound:
            table = self.client.create_table(Table(table_ref=table_id, schema=self.table_schema))
        return table

    # get latest date
    # return tuple(number of rows, result)
    def get_latest_date_dict(self, client_name:str):
        result = self.client.query(
            queries.find_latest_date.format(PROJECT_NAME, client_name, TABLE_NAME)
        ).result()

        return (result.total_rows, result)

    def get_dataset_list(self):
        return [dataset.dataset_id for dataset in list(self.client.list_datasets())]