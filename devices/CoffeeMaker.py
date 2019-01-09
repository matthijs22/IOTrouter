import requests


class CoffeeMaker:
    def __init__(self, name, ip):
        self.name = name
        self.ip = ip

    def brew(self, params):
        try:
            size = params['size']
            # requests.get("http://" + self.ip + "/brew/"+size)
            return "OK"
        except requests.RequestException as e:
            print(e)
            return "ERROR"

    def toggle(self, params):
        try:
            state = params['state']
            # requests.get("http://" + self.ip + "/"+state)
            return "OK"
        except requests.RequestException as e:
            print(e)
            return "ERROR"
