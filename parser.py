import yaml

class ConfigParser:
    def __init__(self):
        self.pins = {}
        self.encoders = {}
        self.translation = {}
        self.settings = {}
        self.parse()

    def parse(self):
        with open('config.yml') as file:
            content = yaml.full_load(file)

        for h1, h2 in content.items():
            if h1 == "pins":
                self.pins = h2
            if h1 == "encoders":
                self.encoders = h2
            if h1 == "translation":
                self.translation = h2
            if h1 == "settings":
                self.settings = h2

        file.close()
