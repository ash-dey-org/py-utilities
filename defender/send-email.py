# to do
# send email with attachment
# https://learn.microsoft.com/en-us/azure/communication-services/quickstarts/email/send-email-advanced/send-email-with-attachments?tabs=connection-string&pivots=programming-language-python
# send email using app resgistration

# pip install azure-identity
# pip install azure-communication-identity
# pip install azure-communication-email

import os
import base64
from azure.communication.email import EmailClient
# from azure.identity import DefaultAzureCredential

# To use Azure Active Directory Authentication (DefaultAzureCredential) make sure to have AZURE_TENANT_ID, AZURE_CLIENT_ID and AZURE_CLIENT_SECRET as env variables.

connection_string = os.environ.get('CON_STR')

with open("./defender_log_20231113.csv", "rb") as file:
    file_bytes_b64 = base64.b64encode(file.read())

message = {
    "content": {
        "subject": "This is the subject",
        "plainText": "This is the body",
        "html": "<html><h1>This is the body</h1></html>"
    },
    "recipients": {
        "to": [
            {
                "address": "ashabc@hotmail.com",
                "displayName": "Ash Dey"
            }
        ]
    },
    "senderAddress": "DoNotReply@9a80dbdd-e3ba-4c7d-9ffb-9a5e953179a6.azurecomm.net",
    "replyTo": [
        {
            "address": "ash.dey@standards.org.au",  # Email address. Required.
            "displayName": "Ash Dey"  # Optional. Email display name.
        }
    ],
    "attachments": [
        {
            "name": "defender-report",
            "contentType": "text/csv",
            "contentInBase64": file_bytes_b64.decode()
        }
    ]
}


POLLER_WAIT_TIME = 10

try:
    # endpoint = "https://central-communication-service.australia.communication.azure.com"
    # email_client = EmailClient(endpoint, DefaultAzureCredential())
    email_client = EmailClient.from_connection_string(connection_string)

    poller = email_client.begin_send(message);

    time_elapsed = 0
    while not poller.done():
        print("Email send poller status: " + poller.status())

        poller.wait(POLLER_WAIT_TIME)
        time_elapsed += POLLER_WAIT_TIME

        if time_elapsed > 18 * POLLER_WAIT_TIME:
            raise RuntimeError("Polling timed out.")

    if poller.result()["status"] == "Succeeded":
        print(f"Successfully sent the email (operation id: {poller.result()['id']})")
    else:
        raise RuntimeError(str(poller.result()["error"]))

except Exception as ex:
    print(ex)
