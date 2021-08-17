# Изучить список открытых API. Найти среди них любое, требующее авторизацию (любого типа).
# Выполнить запросы к нему, пройдя авторизацию. Ответ сервера записать в файл.

#Токен на сутки (!!!)
#https://oauth.vk.com/blank.html#access_token=691bf4f8ae30e6de87f48234342cb500fd044588df3b6a0d80ce42c1c30028662fad5a53c30dda231d8e5&expires_in=86400&user_id=256645318

import requests
import json
from pprint import pprint

method = 'wall.get'
url = 'https://api.vk.com/method/'+method
token = '691bf4f8ae30e6de87f48234342cb500fd044588df3b6a0d80ce42c1c30028662fad5a53c30dda231d8e5'
version = 5.131

params = {
    'owner_id': -33654179,
    'count': 10,
    'access_token': token,
    'v': version}


response = requests.get(url, params=params)
vk_json = response.json()

with open('vk_json.json', 'w') as f:
    json.dump(vk_json, f)

#pprint(vk_json)

#Выведем только содержание постов

for i in vk_json:
    a = vk_json['response']['items']
    for elem in a:
        print(elem.get('text'))
        print(f'\n*END*\n')



