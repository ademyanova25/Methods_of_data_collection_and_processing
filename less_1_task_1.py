# Посмотреть документацию к API GitHub, разобраться как вывести список репозиториев для конкретного
# пользователя, сохранить JSON-вывод в файле *.json.

import requests
import json

username = 'ademyanova25'
url = 'https://api.github.com/users/'+username+'/repos'
response = requests.get(url)

with open('r_json.json', 'w') as f:
    json.dump(response.json(), f)

print('Список репозиториев:')
for i in response.json():
    print(i['name'])


