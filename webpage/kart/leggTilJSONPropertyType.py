import json
import pandas as pd

with open('norskeKommunerBareEnheter.json', 'r') as f:
    data = json.load(f)
    for feature in data['features']:
        feature['type'] = "Feature"


with open('norskeKommunerBareEnheterMedFeature.json', 'w') as f:
    json.dump(data, f)
