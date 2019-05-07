#!/usr/bin/python3

import muckrock_sdk as mr_sdk

mr = mr_sdk.Muckrock()

subject = "Email Metadata"
body = """
To Whom It May Concern:

Pursuant to the Delaware Freedom of Information Act, I hereby request the following records:

Metadata of all emails sent from any email services managed by this department. Please limit the scope of this request to January, 2017.

I am only interested in the following metadata:
from email address,
to email addresses,
cc email addresses,
bcc email addresses
time, and date.

The requested documents will be made available to the general public, and this request is not being made for commercial purposes.

In the event that there are fees, I would be grateful if you would inform me of the total charges in advance of fulfilling my request. I would prefer the request filled electronically, by e-mail attachment if available or CD-ROM if not.

Thank you in advance for your anticipated cooperation in this matter. I look forward to receiving your response to this request within 15 business days, as the statute requires.

Sincerely,
Matt Chapman
"""

resp = mr.send_request(subject, body, 236, 4843, prompt=True)
