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
