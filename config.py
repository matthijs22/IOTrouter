import json


class Config:
    _config = {}

    def __init__(self):
        with open('config.json') as f:
            self._config = json.load(f)

    def __getattr__(self, name):
        return self._config[name]

