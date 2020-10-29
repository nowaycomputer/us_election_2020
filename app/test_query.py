import requests
import json

url = 'http://127.0.0.1:5000/api/'

headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
r = requests.post(url, headers=headers)

print(r, r.text)