import requests


class Curtain:
    def __init__(self, name, ip):
        self.name = name
        self.ip = ip

    def toggle(self, params):
        try:
            state = params['state']
            # requests.get("http://" + self.ip + "/"+state)
            return "OK"
        except requests.RequestException as e:
            return "ERROR"
