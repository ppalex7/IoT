import json
import time

import requests

def lambda_handler(event, context):
    # TODO implement
    return {
        'statusCode': 200,
        'body': 'lambda_result'
    }


def submit_meters(cold, hot):
    username = "TODO"   # fetch from secrets
    password = "TODO"   # same

    r = requests.post('https://onewind.mosvodokanal.ru/api/login', data = {'username': username, 'password': password, 'captcha': ''})

    r2 = requests.get('https://onewind.mosvodokanal.ru/api/ReportFormData/get', params={'_dc': str(int(time.time()*1000)), 'reportId': 'NATURAL_PERSON_USER_ACCOUNT_REGISTER', 'page': 1, 'start': 0, 'limit': 25}, cookies=r.cookies, headers={'Referer': 'https://onewind.mosvodokanal.ru/'})
    account_id = r2.json()['list'][0]['ID']

    r3 = requests.post('https://onewind.mosvodokanal.ru/api/NewMeterReadRequest/getOrCreateMeterReadRequest', cookies=r.cookies, headers={'Referer': 'https://onewind.mosvodokanal.ru/'}, data={'accountId': account_id})
    request_id = r3.json()['requestId']
    param_list = [{"type":"REQUEST_ID","value":request_id}]

    r4 = requests.post('https://onewind.mosvodokanal.ru/api/ReportFormData/get', params={'_dc': str(int(time.time()*1000))}, data={'reportId': 'NATURAL_PERSON_METER_READ_REQUEST_PART_DATA_REESTR', 'parameterList': json.dumps(param_list)}, cookies=r.cookies, headers={'Referer': 'https://onewind.mosvodokanal.ru/'})
    ## CHECK WATER_TYPE_ABBR
    cold_id = r4.json()['list'][0]['ID']
    hot_id = r4.json()['list'][1]['ID']
    event_code = r4.json()['list'][0]['REGISTER_POINT_EVENT_TYPE_CODE']
    req_data = {"accountId":account_id,"skipValidation":False,"meterReadDataPartBeans":[{"id":cold_id,"requestElementId":cold_id,"eventTypeCode":event_code,"commentId":None,"fileId": None, "meterReadingValue":45},{"id":hot_id,"requestElementId":hot_id,"eventTypeCode":event_code,"commentId":None,"meterReadingValue":22,"fileId":None}]}

    r5 = requests.post('https://onewind.mosvodokanal.ru/api/NaturalPersonMeterRead/send', cookies=r.cookies, headers={'Referer': 'https://onewind.mosvodokanal.ru/'}, json=req_data)
