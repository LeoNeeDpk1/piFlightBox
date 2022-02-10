import yaml

class ConfigParser:
    def __init__(self):
        self.encoders = {}
        self.parse()

    def parse(self):
        with open('config.yml') as file:
            content = yaml.full_load(file)

        for h1, h2 in content.items():
            if h1 == "encoders":
                self.encoders = h2

        print("Config parsing complete!")