#!/usr/bin/python3

import muckrock_sdk

mr = muckrock_sdk.Muckrock()

username = 'ChapFOIA'

my_requests = mr.user_requests(username)


def save_file

for req in my_requests:
    communications = req.communications
    for comm in communications:
        comm_files = comm.download_files()
        for f in comm_files:
            
