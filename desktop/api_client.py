import requests


class APIClient:
    BASE_URL = 'http://127.0.0.1:8000/api/'

    def __init__(self):
        self.token = None
        self.refresh_token = None

    def login(self, username, password):
        try:
            resp = requests.post(
                f'{self.BASE_URL}token/',
                json={'username': username, 'password': password},
                timeout=5
            )
            if resp.status_code == 200:
                data = resp.json()
                self.token = data['access']
                self.refresh_token = data['refresh']
                return True, None
            return False, resp.json().get('detail', 'Ошибка входа')
        except requests.exceptions.ConnectionError:
            return False, 'Сервер недоступен'

    def _refresh(self):
        if not self.refresh_token:
            return False
        try:
            resp = requests.post(
                f'{self.BASE_URL}token/refresh/',
                json={'refresh': self.refresh_token}
            )
            if resp.status_code == 200:
                self.token = resp.json()['access']
                return True
        except requests.exceptions.ConnectionError:
            pass
        return False

    def _headers(self):
        return {'Authorization': f'Bearer {self.token}'} if self.token else {}

    def _request(self, method, endpoint, **kwargs):
        resp = method(f'{self.BASE_URL}{endpoint}', headers=self._headers(), **kwargs)
        if resp.status_code == 401 and self._refresh():
            resp = method(f'{self.BASE_URL}{endpoint}', headers=self._headers(), **kwargs)
        return resp

    def get(self, endpoint, params=None):
        return self._request(requests.get, endpoint, params=params)

    def post(self, endpoint, data):
        return self._request(requests.post, endpoint, json=data)

    def put(self, endpoint, data):
        return self._request(requests.put, endpoint, json=data)
    
    def patch(self, endpoint, data):
        return self._request(requests.patch, endpoint, json=data)

    def delete(self, endpoint):
        return self._request(requests.delete, endpoint)