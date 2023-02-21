import boto3
import json
import logging
import os

from botocore.config import Config

logger = logging.getLogger()
logger.setLevel(logging.INFO)

session = boto3.session.Session()
timestream_config = Config(
    read_timeout=20,
    region_name='eu-central-1',
    max_pool_connections=50,
    retries={'max_attempts': 10}
)
query_client = session.client('timestream-query')


def lambda_handler(event, context):
    stat = fetch_stat()
    return {
        'statusCode': 200,
        'body': json.dumps(stat),
        'cold': stat['cold']['last'] / 1000,
        'hot': stat['hot']['last'] / 1000
    }


def fetch_stat():
    query = """
        SELECT water_temperature
            , MAX_BY(measure_value::bigint, time) AS last
            , MIN_BY(measure_value::bigint, time) AS first
        FROM "{}"."{}" WHERE time > ago(30d)
            AND "water_temperature" IN ('cold', 'hot')
        GROUP BY water_temperature
    """.strip().format(os.environ['DATABASE_NAME'], os.environ['TABLE_NAME'])
    res = query_client.query(QueryString=query)
    if res['ResponseMetadata']['HTTPStatusCode'] != 200:
        logger.error("TimestreamQuery failed, response: %s", res)
        raise Exception("TimestreamQuery response is not OK")
    logger.info("QueryStatus: %s", res['QueryStatus'])
    data = dict([parse_row(row) for row in res['Rows']])
    logger.info("Parsed data: %s", data)
    return data


def parse_row(row):
    data = [v['ScalarValue'] for v in row['Data']]
    return (data[0], {'last': int(data[1]), 'first': int(data[2])})
