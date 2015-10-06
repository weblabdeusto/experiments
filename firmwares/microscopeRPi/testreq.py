import requests
import json

headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

data = {'direction':'right','dist':1, 'axis': 'x'}
data = json.dumps(data)

resp = requests.post('http://localhost:8082/move', data=data, headers=headers)

print resp.content
