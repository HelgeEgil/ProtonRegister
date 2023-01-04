import json
import pandas as pd

df = pd.read_csv("kommuner.csv", sep=",", header=0)

unique_enheter = sorted(df["Stråleterapienhet"].unique())
unique_HF = sorted(df["HF"].unique())
unique_RHF = sorted(df["RHF"].unique())

enum_enheter = {v: k for k, v in enumerate(unique_enheter)}
enum_HF = {v: k for k, v in enumerate(unique_HF)}
enum_RHF = {v: k for k, v in enumerate(unique_RHF)}

with open('norskeKommuner.json', 'r') as f:
    data = json.load(f)
    for feature in data['features']:
        kommunenr = feature['properties']['kommunenummer']
        kommunenavn = feature['properties']['navn']
        dff = df[df["Kommunenr"] == kommunenr]
        enhet = dff["Stråleterapienhet"].values[0]
        HF = dff["HF"].values[0]
        RHF = dff["RHF"].values[0]
        bergenoslo = RHF in ("Helse Sør-Øst", "Helse Midt-Norge") and 1 or 0

        fylkenr = dff["Fylkenr"].values[0]
        feature['properties']['enhet'] = int(enum_enheter[enhet])
        feature['properties']['HF'] = int(enum_HF[HF])
        feature['properties']['RHF'] = int(enum_RHF[RHF])
        feature['properties']['fylke'] = int(fylkenr)
        feature['properties']['bergenoslo'] = int(bergenoslo)

with open('norskeKommunerMedHelseinfoSomTallMedBergenOslo.json', 'w') as f:
    json.dump(data, f)
