#!/usr/bin/python3

import requests

from os import environ
from time import sleep

def state_abbrevs():
    ['AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
     'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA',
     'ME', 'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT',
     'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND',
     'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN',
     'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY']

def json_from_url(url):
    headers = get_headers()
    resp = requests.get(url, headers=headers)

    status = resp.status_code
    if status != 200:
        print("Request to %s failed with %s" % (url, status))
        sleep(1)
        return None

    try:
        resp_json = resp.json()
    except:
        print("Failed to parse json from %s" % url)
        resp_json = []

    sleep(1)

    return resp_json

def token_from_file(filepath=None):
    if not filepath:
        homepath = environ['HOME']
        filepath = "%s/%s" % (homepath, '.muckrock_token')

    fh = open(filepath)
    token = fh.readline().rstrip()
    fh.close()

    return token

def muckrock_token(username=None, password=None):
    if not username or not password:
        token = token_from_file()

    else:
        resp = get_api_key()
        auth_str = resp['Authorization']
        token = auth_str.split()[1]

    return token

def user_requests(username):
    base_url = 'https://www.muckrock.com/api_v1/foia'
    url = "%s?user=%s" % (base_url, username)

    ret = json_from_url(url)['results']
    return ret

def request_juris(juris_id):
    endpoint_base = 'https://www.muckrock.com/api_v1/jurisdiction'
    url = '%s/%s' % (endpoint_base, juris_id)
    ret = json_from_url(url)

    return ret

def request_agency(agency_id):
    endpoint_base = 'https://www.muckrock.com/api_v1/agency'
    url = '%s/%s' % (endpoint_base, agency_id)
    ret = json_from_url(url)

    return ret

def get_headers():
    headers = {'Authorization': 'Token %s' % muckrock_token(),
                'content-type': 'application/json'}

    return headers
