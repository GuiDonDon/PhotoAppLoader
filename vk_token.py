import requests
from tqdm import tqdm
import json
import datetime

class VK:

   def __init__(self, access_token, user_id, version='5.131'):
       self.token = access_token
       self.id = user_id
       self.version = version
       self.params = {'access_token': self.token, 'v': self.version}

   def _photos_info(self):
       url = 'https://api.vk.com/method/photos.get'
       params = {'owner_id': int(self.id), 
                 'album_id': 'profile',
                 'extended': 1,
                 'photo_sizes': 1}
       photos_info = requests.get(url=url, params={**self.params, **params}).json()['response']
       profile_photos_url = []
       for photo in photos_info['items']:
            photo_url, size = find_max_size(photo['sizes'])
            profile_photos_url.append(
                {
                    'likes': photo['likes']['count'],
                    'type': size,
                    'url': photo_url,
                    'date': photo['date']
                }
            )
       return profile_photos_url
   
class YaDisck:
    def __init__(self, token: str):
        self.token = token
        self.json = []

    def get_headers(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': 'OAuth {}'.format(self.token)
        }

    def create_folder_yadisck(self, folder_name):
        params = {'path': 'disk:/{}/'.format(folder_name)}
        headers = self.get_headers()
        url = 'https://cloud-api.yandex.net/v1/disk/resources'
        response = requests.put(url, headers=headers, params=params)
        response.raise_for_status
        return folder_name

    def download_yandex_disk(self, folder_name, url_download_photos):
        diсt_names = []
        headers = self.get_headers()
        url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
        print('Загружаем фотографии')
        for urls in tqdm(url_download_photos):
            if urls['likes'] not in diсt_names:
                diсt_names.append(urls['likes'])
                path = 'disk:/{}/{}.jpg'.format(folder_name, urls['likes'])
                self.json.append({'file_name': urls['likes'], 'size': urls['type']})
            else:
                diсt_names.append(urls['likes'])
                value = datetime.datetime.fromtimestamp(urls["date"])
                path = 'disk:/{}/{}{}.jpg'.format(
                    folder_name, urls['likes'], f"{value:-%Y-%m-%d}"
                )
                self.json.append({'file_name': f"{urls['likes']}(id{urls['id']})", 'size': urls['type']})
            params = {'path': path, 'url': urls['url']}
            requests.post(url, headers=headers, params=params)
        print('Фотографии загружены')


   
def find_max_size(dict_sizes):
    max_size = 0
    max_elem = 0
    for j in range(len(dict_sizes)):
        file_dpi = dict_sizes[j].get('width') * dict_sizes[j].get('height')
        if file_dpi > max_size:
            max_size = file_dpi
            max_elem = j
    return dict_sizes[max_elem].get('url'), dict_sizes[max_elem].get('type')
   


if __name__ == '__main__':
    access_token = input('Введите токен приложения ВК: ') 
    user_id = input('Введите ID пользователя ВК: ') 
    ya_token = input('Введите токен Я.Диска: ') 
    vk = VK(access_token, user_id)
    ya_disk = YaDisck(ya_token)
    folder_name = ya_disk.create_folder_yadisck('vk')
    urls_photo = vk._photos_info()
    ya_disk.download_yandex_disk(folder_name, urls_photo)
    with open('VK_photos.json', 'w') as outfile:  
        json.dump(ya_disk.json, outfile)