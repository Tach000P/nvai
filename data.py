import json, os

COOKIES_JSON = os.environ.get('COOKIES_JSON', '{}')
cookies = json.loads(COOKIES_JSON)

GROUP_ID = 352
MY_USER_ID = 8724
QUEUE_FILE = "queue.json"  # файл для сохранения очереди
FUNCTIONS = ["/randomUser", "/randomNum", "/allUsers", "/about", "/rules", "/help",]

# cookies = {
#     '_ym_d': '1756738619',
#     '_ym_isad': '1',
#     '_ym_uid': '1756738619329102790',
#     'auth_key': 'YxDxc4DVW5P%2BUJ%2Fly137XgxIAx9pKZd2m3Re%2BtspieUjWfPn%2FKcSdRmunFhMCxMU',
#     'beget': 'begetok',
#     'device_id': '0f3714b36a0da8298ec4eac27dfd623f',
#     'first_id': '8724',
#     'PHPSESSID': '650baa3c210b16886e8703a454ffe8d5',
#     'theme': 'dark',
# }

