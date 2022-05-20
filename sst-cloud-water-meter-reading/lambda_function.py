import boto3
import json
import os

import requests


session = boto3.session.Session()


def lambda_handler(event, context):
    api = SSTCloudApi()
    houses = api.call('/houses/')
    house_id = houses[0]['id']

    counters = api.call('/houses/{id}/counters/', id=house_id)

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!'),
        'res': counters,
    }


class SSTCloudApi(object):
    def __init__(self, arg):
        secret_name = os.environ['TOKEN_SECRET_NAME']

        client = session.client(service_name='secretsmanager')
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)

        self.token = get_secret_value_response['SecretString']


    def call(self, path, **kwargs):
        url = ('https://api.sst-cloud.com' + path).format(**kwargs)
        authorization = {'Authorization': 'Token {token}'.format(token=token)}

        response = requests.get(url, headers=authorization)
        response.raise_for_status()

        return response.json()
