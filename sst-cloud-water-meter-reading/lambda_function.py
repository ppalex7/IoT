import boto3
import os
import time

import requests

from botocore.config import Config


session = boto3.session.Session()
timestream_config = Config(
    read_timeout=20,
    max_pool_connections=100,
    retries={'max_attempts': 10}
)
write_client = session.client('timestream-write', config=timestream_config)


def lambda_handler(event, context):
    api = SSTCloudApi()
    houses = api.call('/houses/')
    house_id = houses[0]['id']

    counters = api.call('/houses/{id}/counters/', id=house_id)
    data = [{'id': c['id'], 'line': c['line'], 'hot_water': c['for_hot_water'], 'value': c['value'] } for c in counters]

    write_records(data)

    return data


def write_records(data):
    current_time = str(round(time.time()))

    common_attributes = {
        'Dimensions': [
            {'Name': 'service', 'Value': 'water'},
            {'Name': 'location', 'Value': os.environ['LOCATION_DIMENSION_VALUE']},
        ],
        'MeasureName': 'volume',
        'MeasureValueType': 'BIGINT',
        'Time': current_time,
        'TimeUnit': 'SECONDS'
    }

    records = []
    for counter in data:
        temp = 'hot' if counter['hot_water'] else 'cold'
        records.append({
            'MeasureValue': str(counter['value']),
            'Dimensions' : [
                {'Name': 'water_temperature', 'Value': temp},
            ],
        })

    result = write_client.write_records(
        DatabaseName=os.environ['DATABASE_NAME'],
        TableName=os.environ['TABLE_NAME'],
        Records=records,
        CommonAttributes=common_attributes,
        )
    print("WriteRecords Status: [%s]" % result['ResponseMetadata']['HTTPStatusCode'])


class SSTCloudApi(object):
    def __init__(self):
        secret_name = os.environ['TOKEN_SECRET_NAME']

        client = session.client(service_name='secretsmanager')
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)

        self.token = get_secret_value_response['SecretString']

    def call(self, path, **kwargs):
        url = ('https://api.sst-cloud.com' + path).format(**kwargs)
        authorization = {'Authorization': 'Token {token}'.format(token=self.token)}

        response = requests.get(url, headers=authorization)
        response.raise_for_status()

        return response.json()
