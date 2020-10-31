import requests
import json

# For the output based on the latest polls from a set of swing states

url = 'http://127.0.0.1:5000/api/swingstates'
headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
r = requests.post(url, headers=headers)
print(r, r.text)


# For the output based on a single state

# url = 'http://127.0.0.1:5000/api/singlestate'
# data = json.dumps('Florida')
# headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
# r = requests.post(url, data=data, headers=headers)
# print(r, r.text)

# For the output based on the polls from a set of swing states in the past

# url = 'http://127.0.0.1:5000/api/swingstatesdatelimited'
# data={'date': '01/09/2020'}
# data = json.dumps(data)
# headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
# r = requests.post(url, data=data, headers=headers)
# print(r, r.text)
