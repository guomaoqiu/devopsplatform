import requests,json


res = json.loads(requests.get(url="http://ipinfo.io/json").text)['ip']

print res