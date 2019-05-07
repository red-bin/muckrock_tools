#!/usr/bin/python3

import requests
import muckrock_utils as mr_utils
import json

from time import sleep

from shutil import copyfileobj

states_map = {
  'florida':34,
  'pennsylvania':126,
  'tennessee':155,
  'delaware':236,
  'maryland':154,
  'virginia':128,
  'texas':109,
  'ohio':116,
  'arkansas':114,
  'michigan':117,
  'illinois':168,
  'missouri':299,
  'alabama':159,
  'north carolina':153,
  'indiana':152,
  'louisiana':233,
  'montana':157,
  'connecticut':53,
  'alaska':235,
  'arizona':78,
  'california':52,
  'hawaii':247,
  'idaho':228,
  'iowa':246,
  'maine':13,
  'massachusetts':1,
  'nebraska':300,
  'new hampshire':81,
  'new jersey':229,
  'new york':16,
  'north dakota':232,
  'colorado':127,
  'georgia':230,
  'kansas':111,
  'kentucky':147,
  'minnesota':156,
  'mississippi':231,
  'nevada':301,
  'new mexico':227,
  'oklahoma':248,
  'oregon':158,
  'rhode island':82,
  'south carolina':302,
  'south dakota':303,
  'utah':234,
  'vermont':80,
  'washington':54,
  'west virginia':304,
  'wisconsin':146,
  'wyoming':305,
}

class Jurisdiction():
    def __init__(self, id, name, slug, abbrev, 
                 level, parent, public_notes, absolute_url,
                 average_response_time, fee_rate, success_rate):
            self.id = id
            self.name = name
            self.slug = slug
            self.abbrev = abbrev
            self.level = level
            self.parent = parent
            self.public_notes = public_notes
            self.absolute_url = absolute_url
            self.average_response_time = average_response_time
            self.fee_rate = fee_rate
            self.success_rate = success_rate
            self.state = self.absolute_url.split('/')[-3]

            self.agencies = []

class Agency():
    def __init__(self, **xargs):
        self.__dict__.update(xargs)

class Communication():
    def __init__(self, **xargs):
        self.__dict__.update(xargs)

#TODO: declunkify this
class Request():
    def __init__(self, **xargs):
        self.__dict__.update(xargs)
        self.communications = self.create_communications(xargs['communications'])

        #self.raw_email = self.get_raw_email()

    def get_raw_email(self):
        url = 'https://www.muckrock.com/foi/raw_email/%s/' % self.id
        resp = requests.get(url)

        return resp.json()

    def create_communications(self, comms):
        ret_comms = []
        for comm_json in comms:
            new_comm = Communication(**comm_json)
            ret_comms.append(new_comm)

        return ret_comms

    def doc_txt_stream(self, doc_id):
        sleep(1)
        doccloud_id = doc_id.split('-')[0]
        doccloud_file = '-'.join(doc_id.split('-')[1:])

        if not doccloud_id or not doccloud_file:
            return None

        doccloud_url = "https://assets.documentcloud.org/documents/{}/{}.txt"
        doccloud_url = doccloud_url.format(doccloud_id, doccloud_file)

        print("Downloading ", doccloud_url)

        #add error checking
        try:
            response = requests.get(doccloud_url, stream=True)
            return response.raw

        except:
            print("No doccloud file for ", doccloud_url)
            return None

    def download_files(self, save_dir='/tmp/', inc_doccloud=True):
        from os import makedirs
        save_dir = '{}/{}'.format(save_dir, self.id)
        makedirs(save_dir, exist_ok=True)

        for comm in self.communications:
            for comm_file in comm.files:
                response = requests.get(comm_file['ffile'], stream=True, timeout=5)
                filename = comm_file['ffile'].split('/')[-1]

                savepath = '{}/{}'.format(save_dir, filename)

                with open(savepath, 'wb') as out_file:
                    copyfileobj(response.raw, out_file)

                if inc_doccloud:
                    txt_stream = self.doc_txt_stream(comm_file['doc_id'])
                    txt_path = "{}.documentcloud.txt".format(savepath)

                    if txt_stream:
                        with open(txt_path, 'wb') as out_file:
                            copyfileobj(txt_stream, out_file)

class Muckrock():
    def __init__(self):
        self.jurisdictions = []

        self.token = mr_utils.muckrock_token()
        self.agencies = []
        self.jurisdictions = []
        self.states = []
        self.requests = []

    def muckrock_states(self):
        if self.states:
            return self.states

        base_url = 'https://www.muckrock.com/api_v1/jurisdiction'
        url = "%s/?level=s" % base_url 

        resp = mr_utils.json_from_url(url)
        self.states = resp

        jurisdictions = [ self.juris_by_id(s) for s in self.states ]
       
        return jurisdictions

    def juris_children(self, juris_id):
        base_url = 'https://www.muckrock.com/api_v1/jurisdiction'
        url = '{}/?parent={}'.format(base_url, juris_id)

        results = mr_utils.json_from_url(url)

        ret_jurisdictions = []
        for juris_data in results:
            juris = Jurisdiction(**juris_data)
            ret_jurisdictions.append(juris)
         
        return ret_jurisdictions

    def request_by_id(self, request_id):
        cached_request = self.request_exists(request_id)
        if cached_request:
            return cached_request

        url = 'https://www.muckrock.com/api_v1/foia/%s/' % request_id
        results = mr_utils.json_from_url(url)
        
        new_request = Request(**results)

        self.requests.append(new_request)

        return new_request
    
    def is_juris_state(self, juris_id):
        poss = [ s for s in self.muckrock_states() if juris_id == s['id'] ]
        if poss and len(poss) == 1:
            return True

        else:
            return False

    def juris_by_id(self, juris_id):
        for juris in self.jurisdictions:
            if juris.id == juris_id:
                return juris

        juris_details = mr_utils.request_juris(juris_id)
        ret_juris = Jurisdiction(**juris_details)
        self.jurisdictions.append(ret_juris)

        return ret_juris

    def agency_by_id(self, agency_id):
        for agency in self.agencies:
            if agency.id == agency_id:
                return agency

        agency_details = mr_utils.request_agency(agency_id)
        ret_agency = Agency(**agency_details)
        self.agencies.append(ret_agency)

        return ret_agency

    def is_agency_cached(self, agency_id):
        for agency in self.agencies:
            if agency.id == agency_id:
                return True

        return False

    def is_juris_cached(self, juris_id):
        for juris in self.jurisdictions:
            if juris.id == juris_id:
                return True

        return False

    def agency_search(self, name='', status='', juris_id='',
                      types_name='', requires_proxy=''):
        base_url = 'https://www.muckrock.com/api_v1/agency'
        url_format = '%s/?name=%s&status=%s&jurisdiction=%s&types=%s'
        url = url_format % (base_url, name, status, juris_id, types_name)

        results = mr_utils.json_from_url(url)

        ret = []
        for agency in results:
            agency_id = agency['id']
            if not self.is_agency_cached(agency_id):
                agency_obj = Agency(**agency)
                self.agencies.append(agency_obj)
            else:
                agency_obj = self.agency_by_id(agency_id)

            ret.append(agency_obj)

        return ret

    def juris_search(self, name='', abbrev='', level='', parent='', state_name=None, fetch_agencies=True):
        if state_name and not parent:
            state_name = state_name.lower()
            if state_name in states_map:
                parent = states_map[state_name]

        base_url = 'https://www.muckrock.com/api_v1/jurisdiction'
        url_format = '{}/?name={}&abbrev={}&level={}&parent={}'
        url = url_format.format(base_url, name, abbrev, level, parent)
       
        results = mr_utils.json_from_url(url)

        jurisdictions = []
        for juris in results:
            juris_id = juris['id']
            if not self.is_juris_cached(juris_id):
                juris_obj = Jurisdiction(**juris)
                self.jurisdictions.append(juris_obj)
            else:
                juris_obj = self.juris_by_id(juris_id)

            jurisdictions.append(juris_obj)

        if fetch_agencies:
            for juris in jurisdictions:
                juris_agencies = self.agencies_by_juris_id(juris.id)
                for agency in juris_agencies:
                    if agency not in juris.agencies:
                        juris.agencies.append(agency)

        return jurisdictions 

    def agencies_by_juris_id(self, juris_id):
        return self.agency_search(juris_id=juris_id)

    def juris_exists(self, juris_id):
        for cached_juris in self.jurisdictions:
            if cached_juris.id == juris_id:
                return cached_juris

        return None

    def request_exists(self, request_id):
        for cached_request in self.requests:
            if cached_request.id == request_id:
                return cached_request

        return None

    #Takes a long time and is NOT optimized.
    def all_requests(self):
        url = 'https://www.muckrock.com/api_v1/foia?page_size=100'
        ret = mr_utils.json_from_url(url)

        return ret

    def all_communications(self):
        url = 'https://www.muckrock.com/api_v1/communication?page_size=10000'
        ret = mr_utils.json_from_url(url)

        return ret

    def all_jurisdictions(self):
        url = 'https://www.muckrock.com/api_v1/jurisdiction?page_size=10000'
        ret_jurisdictions = mr_utils.json_from_url(url)

        for juris in ret_jurisdictions:
            if not self.juris_exists(juris['id']):
                juris_obj = Jurisdiction(**juris)
                self.jurisdictions.append(juris_obj)

        return self.jurisdictions

    def user_requests(self, username):
        base_url = 'https://www.muckrock.com/api_v1/foia'
        url = "%s?user=%s" % (base_url, username)
    
        requests_ret = []

        results = mr_utils.json_from_url(url)
        for request_json in results:
            request_id = request_json['id']
            cached_request = self.request_exists(request_id)
            if cached_request:
                requests_ret.append(cached_request)
            else:
                new_request = Request(**request_json)
                requests_ret.append(new_request)
                self.requests.append(new_request)
       
        return requests_ret

    def request_search(self, title='', user='', agency_id=''):
        base_url = 'https://www.muckrock.com/api_v1/foia'
        url_format = '{}/?title={}&user={}&agency={}'
        url = url_format.format(base_url, title, user, agency_id)

        results = mr_utils.json_from_url(url)

        requests_ret = []

        for request_json in results:
            request_id = request_json['id']
            cached_request = self.request_exists(request_id)
            if cached_request:
                requests_ret.append(cached_request)
            else:
                new_request = Request(**request_json)
                requests_ret.append(new_request)
                self.requests.append(new_request)
 
        return requests_ret

    def send_request(self, subject, body, juris_id, agency_id, prompt=False):
        base_url = 'https://www.muckrock.com/api_v1/foia/'

        agency = self.agency_by_id(agency_id)
        jurisdiction = self.juris_by_id(juris_id)

        data = {'title': subject, 
                'full_text': body,
                'document_request': body,
                'jurisdiction': juris_id, 
                'embargo': False,
                'agency': agency_id}

        print("Submitting to: %s - %s" 
                % (agency.name, jurisdiction.name))

        json_data = json.dumps(data)
        headers = mr_utils.get_headers()

        if prompt:
            yn = input('Continue? (Y/N)\n')
            if yn not in ['y','Y']:
                print('Exiting!')
                exit(1)

        print(headers)
        print()
        print(json_data)
        print()
        resp = requests.post(base_url, headers=headers, data=json_data)
        return resp

    def send_batch_request(self, subject, body, agencies, prompt=True):
        """agency_mappings must be in the format of: ([juris_id, agency_id], [juris_id, agency_id])"""

        print("Sending the following request:")
        print("======Subject======")
        print()
        print("======Body======")
        print(body)
        print()
        print("======Agencies======")
        for agency in agencies:
            print(agency.name)
       
        if prompt:
            while True:
                yn = input('Continue? (Y/N)\n')
                if yn in ['n','N']:
                    print('Exiting!')
                    exit(1)

                elif yn in ['Y', 'y']:
                    break

                else:
                    print("You must choose either Y or N")


        for agency in agencies:
            self.send_request(subject, body, a.jurisdiction, a.id)
