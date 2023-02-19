import json
import logging
import os
import time

import requests


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def lambda_handler(event, context):
    r = submit_meters(50, 24)
    return {
        'statusCode': 200,
        'body': """
            Показания отправлены в Мосводоканал.
            Ответ: {}
        """.strip().format(json.dumps(r)),
    }


def dc():
    return str(int(time.time() * 1000))


def readDataBean(id, event_type, volume):
    return {
        'id': id,
        'requestElementId': id,
        'eventTypeCode': event_type,
        'commentId': None,
        'fileId': None,
        'meterReadingValue': volume,
    }


def submit_meters(cold, hot):
    api_url = 'https://onewind.mosvodokanal.ru/'
    report_url = api_url + 'api/ReportFormData/get'

    auth_data = {
        'username': os.environ['LOGIN'],
        'password': os.environ['PASSWORD'],
        'captcha': '',
    }
    r_auth = requests.post(api_url + 'api/login', data=auth_data)
    r_auth.raise_for_status()
    if (r_auth.status_code != 200
        or 'authenticated' not in r_auth.json()
        or not r_auth.json()['authenticated']):
        raise Exception('Authorization failed: ' + r_auth.text)
    ch = {'cookies': r_auth.cookies, 'headers': {'Referer': api_url}}

    r_account = requests.get(report_url, params={'_dc': dc(), 'reportId': 'NATURAL_PERSON_USER_ACCOUNT_REGISTER', 'page': 1, 'start': 0, 'limit': 25}, **ch)
    logger.debug("Got NATURAL_PERSON_USER_ACCOUNT_REGISTER report: %d, %s", r_account.status_code, r_account.content)
    r_account.raise_for_status()
    account_id = r_account.json()['list'][0]['ID']

    r_readreq = requests.post(api_url + 'api/NewMeterReadRequest/getOrCreateMeterReadRequest', data={'accountId': account_id}, **ch)
    logger.debug("MeterReadRequest response: %d, %s", r_readreq.status_code, r_readreq.content)
    r_readreq.raise_for_status()
    request_id = r_readreq.json()['requestId']
    param_list = [{'type': 'REQUEST_ID', 'value': request_id}]

    r_meters = requests.post(report_url, params={'_dc': dc()}, data={'reportId': 'NATURAL_PERSON_METER_READ_REQUEST_PART_DATA_REESTR', 'parameterList': json.dumps(param_list)}, **ch)
    logger.debug("Got NATURAL_PERSON_METER_READ_REQUEST_PART_DATA_REESTR response: %d, %s", r_meters.status_code, r_meters.content)
    r_meters.raise_for_status()
    meters = r_meters.json()['list']
    # TODO: separate cold and hot meters by 'WATER_TYPE_ABBR' attribute (hot, cold)
    cold_id = meters[0]['ID']
    hot_id = meters[1]['ID']
    event_code = meters[0]['REGISTER_POINT_EVENT_TYPE_CODE']

    req_data = {
        'accountId': account_id,
        'skipValidation': False,
        'meterReadDataPartBeans': [
            readDataBean(cold_id, event_code, cold),
            readDataBean(hot_id, event_code, hot),
        ]
    }

    submit = requests.post(api_url + 'api/NaturalPersonMeterRead/send', json=req_data, **ch)
    logger.debug("Meters submited: %d, %s", submit.status_code, submit.content)
    submit.raise_for_status()
    return submit.json()
