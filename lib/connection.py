import json
import base64
import requests.auth

class Connection:
    def __init__(self, username=None, password=None, config=None):
        self.username = username
        self.password = password
        self.config = config
        self.ip = 'localhost'
        if self.config is not None:
            self.init_config()

    def init_config(self):
        data = {}
        with open(self.config, 'r') as f:
            data = json.load(f)
        if 'username' in data:
            self.username = data['username']
        if 'password' in data:
            self.password = data['password']
        if 'ip' in data:
            self.ip = data['ip']

    def basic_auth(self):
        return str(base64.b64encode(bytes(f'{self.username}:{self.password}')))

    def requests_auth(self):
        return requests.auth.HTTPBasicAuth(self.username, self.password)
