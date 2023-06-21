import json
from models import Config

with open('msconfig.json') as file:
    config = Config(**json.load(file))
