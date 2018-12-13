#!/usr/bin/python3

import requests
import json

from getpass import getpass
from retrying import retry
from os import environ
from time import sleep

def state_abbrevs():
    ['AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
     'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA',
     'ME', 'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT',
     'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND',
     'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN',
     'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY']


retry_opts = dict(wait_exponential_multiplier=1000, 
                  wait_exponential_max=10000, 
                  stop_max_attempt_number=3)

def get_api_key():
    try:
        token = environ['MUCKROCK_TOKEN']
    except KeyError:
        user = input('Username: ')
        pw = getpass()
        response = requests.post('https://www.muckrock.com/api_v1/token-auth/', data={'username': user, 'password': pw})
        if not response.raise_for_status():
            data = response.json()
            token = data['token']
            environ['MUCKROCK_TOKEN'] = token

    return token

#@retry(**retry_opts)
def get_raw_email(num):
    headers = get_headers()
    url = "https://www.muckrock.com/foi/raw_email/%s/" % num
    resp = requests.get(url, headers=headers)

    return resp

#    try:
    
#    except:
#        return None

def raw_emails(start_num=1, end_num=550000):
    for c in range(start_num, end_num):
        yield resp.json()

def json_from_url(url, data={}):
    print(url)
    headers = get_headers()

    data = json.dumps(data)

   
    while True: 
        try:
            resp = requests.get(url, headers=headers, data=data)
            break
        except:
            print("Sleeping for 20 seconds...")
            sleep(20)
            resp = requests.get(url, headers=headers, data=data)
            break

    status = resp.status_code
    if status != 200:
        print("Request to %s failed with %s" % (url, status))
        sleep(1)
        return None

    resp_json = resp.json()
    print(resp_json)

    sleep(1)

    #recursively grabs all pages
    if resp_json.get('next'):
        resp_json['results'] += json_from_url(next_page)

    if resp_json.get('slug'):
        return resp_json

    return resp_json['results']

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
        token = token_from_file() #get_api_key()

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
