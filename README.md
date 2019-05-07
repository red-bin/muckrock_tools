# muckrock_tools

SDK for sending send requests through muckrock.com.

## Sending Requests

```python
  import muckrock_sdk as mr_sdk

  mr = mr_sdk.Muckrock()
  mr.send_request(subject="ur warez", body="are mine, 
    juris_id=1234, agency_id=5678)
```

## Download Files from Request

```python
  #by default, downloads OCR'd files from documentcloud
  mr = Muckrock() 
  r = mr.request_by_id(62870)  
  r.download_files(savedir='/tmp/')
```

## Download all federal requests' files, including documentcloud:

```python
#!/usr/bin/python3

import muckrock_sdk

mr = muckrock_sdk.Muckrock()

fed_juris = mr.juris_search(level='f', fetch_agencies=False)[0]
fed_agencies = mr.agencies_by_juris_id(fed_juris.id)

requests = []
for agency in fed_agencies:
    print("Grabbing requests for agency: %s" % agency.name)
    agency_requests = mr.request_search(agency_id=agency.id)

    for request in agency_requests:
        print("Downloading request files for %s" % request.slug)
        request.download_files(save_dir='/opt/data/muckrock_dump/')
```
