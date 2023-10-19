import os
import time
import json
# import csv
# import requests
import urllib.request
import urllib.parse


# define environment variables and other fixed parameters
tenantId = os.environ.get('AZURE_TENANT_ID')
appId = os.environ.get('DEFENDER_APP_ID')
appSecret = os.environ.get('DEFENDER_APP_SECRET')
sumourl = os.environ.get('SUMO_COLLECTOR_URL')

url = "https://login.microsoftonline.com/%s/oauth2/token" % (tenantId)

resourceAppIdUri = 'https://api.securitycenter.microsoft.com'

body = {
    'resource' : resourceAppIdUri,
    'client_id' : appId,
    'client_secret' : appSecret,
    'grant_type' : 'client_credentials'
}

# Authenticate to Azure uisng aap client and secret and get token

data = urllib.parse.urlencode(body).encode("utf-8")

req = urllib.request.Request(url, data)
response = urllib.request.urlopen(req)
jsonResponse = json.loads(response.read())
aadToken = jsonResponse["access_token"]

# run query using the token

# simple query
# query = 'DeviceRegistryEvents | limit 10' # Paste your own query here

# complex query
queryFile = open("query.txt", 'r')
query = queryFile.read()
queryFile.close()
# print(query)


url = "https://api.securitycenter.microsoft.com/api/advancedqueries/run"
headers = {
    'Content-Type' : 'application/json',
    'Accept' : 'application/json',
    'Authorization' : "Bearer " + aadToken
}

data = json.dumps({ 'Query' : query }).encode("utf-8")
# print(data)
req = urllib.request.Request(url, data, headers)
response = urllib.request.urlopen(req)
print("getting data from Defender portal, can take appox 10 sec....")
time.sleep(10)
jsonResponse = json.loads(response.read())
schema = jsonResponse["Schema"]
results = jsonResponse["Results"]
# print(results)

# export output from query to a text file containing json array
home_directory = os.path.expanduser("~")
downloads_folder = os.path.join(home_directory, "Downloads")
if not os.path.exists(downloads_folder):
    os.makedirs(downloads_folder)
current_date = time.strftime("%Y%m%d")
filename = f"defender_log_{current_date}.txt"
file_path = os.path.join(downloads_folder, filename)

'''
# write to csv file
outputFile = open(file_path, 'w')
output = csv.writer(outputFile)
output.writerow(results[0].keys())
for result in results:
    output.writerow(result.values())

outputFile.close()

'''

# write output to text file
with open(file_path, "w", encoding="utf-8") as output_file:
    for result in results:
        # Convert each result to a JSON string and write it to the file
        result_json = json.dumps(result, ensure_ascii=False)
        output_file.write(result_json + "\n")
output_file.close()

time.sleep(1)

# upload logs to Sumologic
print("uploading data to sumologic......")
cmd = 'curl -v -X POST -H "X-Sumo-Category:security/defender/hunting" -H "X-Sumo-Name:%s" -T %s %s --ssl-no-revoke' %(file_path, file_path, sumourl)
# print(cmd)
returned_value = os.system(cmd)
# print('returned value:', returned_value)
print("Done.... Check Somologic portal for uploaded data.")


"""
headers = {
    'X-Sumo-Category': 'security/defender/hunting',
}
files = {'file': ('file_path', open(file_path, 'rb'))}
response = requests.post(sumourl, headers=headers, files=files, verify=False)

# Print the response status code and content
print("Response Status Code:", response.status_code)
print("Response Content:", response.text)

"""