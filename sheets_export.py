#!/usr/bin/python3

import gspread
import muckrock_sdk as mr
import muckrock_utils as mr_utils
from oauth2client.service_account import ServiceAccountCredentials

from pprint import pprint
from time import sleep

from os import environ

def summarize_comms(comms_json):
    written_resps = [ c for c in comms_json if not c['autogenerated'] ]
    auto_resps = [ c for c in comms_json if c['autogenerated'] ]

    auto_resp_count = len(auto_resps)
    resp_count = len(written_resps)
    last_comm = written_resps[-1]

    needs_followup = last_comm['response']
    last_comm_body = last_comm['communication']

    ret = { 'resp_count': resp_count,
            'auto_resp_count': auto_resp_count,
            'needs_followup': needs_followup,
            'last_comm_body': last_comm_body }

    return ret

def summarize_request(request_json):
    comms_summary = summarize_comms(request_json['communications'])

    agency_id = request_json['agency']

    juris = sdk.juris_by_id(agency_id)
    agency = sdk.agency_by_id(agency_id)

    parent_id = juris.parent

    summary = {'id': request_json['id'],
               'title': request_json['title'],
               'agency': agency.id,
               'jurisdiction': juris.name,
               'date_submitted': request_json['date_submitted'],
               'slug': request_json['slug'],
               'status': request_json['status'],
               'resp_count': comms_summary['resp_count'],
               'auto_resp_count': comms_summary['auto_resp_count'],
               'needs_followup': comms_summary['needs_followup'],
               'last_comm_body': comms_summary['last_comm_body']}

    return summary

def requests_report(username):
    requests = mr_utils.user_requests(username)
    summarized_requests = [ summarize_request(r) for r in requests[:1] ]

    return summarized_requests

def write_report(report_data, ws):
    headers = ['id', 'title', 'date_submitted', 'slug','status', 
               'agency', 'jurisdiction', 'resp_count', 
               'auto_resp_count', 'needs_followup', 'last_comm_body']

    headers_len = len(headers)
    [ws.update_cell(1, c+1, headers[c]) for c in range(headers_len)]

    for request in report_data:
        cell_vals = [ request[c] for c in headers ]
        ws.append_row(cell_vals)
        sleep(1)

cred_path = '/home/matt/.foia_sheet_creds.json'

scope = ['https://spreadsheets.google.com/feeds']
creds = ServiceAccountCredentials.from_json_keyfile_name(cred_path, scope)

client = gspread.authorize(creds)

sheet_id = ''

#spreadsheet = client.open_by_key(sheet_id)
#worksheet = spreadsheet.get_worksheet(0) 

sdk = mr.Muckrock()


report_data = requests_report('ChapFOIA')
pprint(report_data)
#write_report(report_data, worksheet)