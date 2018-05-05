#!/usr/bin/python3

import muckrock_sdk as mr_sdk

mr = mr_sdk.Muckrock()

subject = "ur warez"
body = "r mine"
juris_id = 169
agency_id = 1234

resp = mr.send_request(subject, body, juris_id, agency_id)
