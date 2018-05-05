#!/usr/bin/python3

import muckrock_sdk

mr = muckrock_sdk.Muckrock()
my_requests = mr.user_requests('ChapFOIA')

for req in my_requests:
    communications = req.communications
    for comm in communications:
        comm_files = comm.download_files()
        for filedata, filename in comm_files:
            fh = open('/tmp/%s' % filename, 'wb')
            fh.write(filedata)
            fh.close()
