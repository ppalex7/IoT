import json
import time

import requests

def lambda_handler(event, context):
    # TODO implement
    return {
        'statusCode': 200,
        'body': 'lambda_result'
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
    username = "TODO"   # fetch from secrets
    password = "TODO"   # same

    api_url = 'https://onewind.mosvodokanal.ru/'
    report_url = api_url + 'api/ReportFormData/get'

    r_auth = requests.post(api_url + 'api/login', data = {'username': username, 'password': password, 'captcha': ''})
    r_auth.raise_for_status()
    if (r_auth.status_code != 200
        or 'authenticated' not in r_auth.json()
        or not r_auth.json()['authenticated']):
        raise Exception('Authorization failed: ' + r_auth.text)
    ch = {'cookies': r_auth.cookies, 'headers': {'Referer': api_url}}

    r_account = requests.get(report_url, params={'_dc': dc(), 'reportId': 'NATURAL_PERSON_USER_ACCOUNT_REGISTER', 'page': 1, 'start': 0, 'limit': 25}, **ch)
    r_account.raise_for_status()
    account_id = r_account.json()['list'][0]['ID']

    r_readreq = requests.post(api_url + 'api/NewMeterReadRequest/getOrCreateMeterReadRequest', data={'accountId': account_id}, **ch)
    r_readreq.raise_for_status()
    request_id = r_readreq.json()['requestId']
    param_list = [{'type': 'REQUEST_ID', 'value': request_id}]

    r_meters = requests.post(report_url, params={'_dc': dc()}, data={'reportId': 'NATURAL_PERSON_METER_READ_REQUEST_PART_DATA_REESTR', 'parameterList': json.dumps(param_list)}, **ch)
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
    submit.raise_for_status()
    return submit.json()
