import pandas as pd
import plotly.graph_objects as go
import json
import numpy as np


def colorbar(zmin, zmax, n=6):
    return dict(
        title="Krefttilfeller",
        tickmode="array",
        tickvals=np.linspace(np.log10(zmin), np.log10(zmax), n),
        ticktext=np.round(10 ** np.linspace(np.log10(zmin), np.log10(zmax), n), 1)
    )


def get_RHF(HF):
    RHF = df_folketall[df_folketall["HF"] == HF]["RHF"].values[0]
    return RHF


def get_kommune_from_nr(nr):
    return df_folketall[df_folketall["Kommunenr"] == nr]["Kommunenavn"].values[0]


def get_fylke_from_kommunenr(nr):
    return df_folketall[df_folketall["Kommunenr"] == nr]["Fylkenavn"].values[0]


def get_HF_from_kommunenr(nr):
    return df_folketall[df_folketall["Kommunenr"] == nr]["HF"].values[0]


def get_RHF_from_kommunenr(nr):
    return df_folketall[df_folketall["Kommunenr"] == nr]["RHF"].values[0]


def get_enhet_From_kommunenr(nr):
    return df_folketall[df_folketall["Kommunenr"] == nr]["Stråleterapienhet"].values[0]


fylkenavn = {30: "Viken", 3: "Oslo", 34: "Innlandet", 54: "Troms og Finnmark", 18: "Nordland", 46: "Vestland", 11: "Rogaland",
             15: "Møre og Romsdal", 50: "Trøndelag", 38: "Vestfold og Telemark", 42: "Agder"}

df_folketall = pd.read_csv("kommuner.csv", header=0, sep=",")
unique_enhet = sorted(df_folketall["Stråleterapienhet"].unique())
unique_HF = sorted(df_folketall["HF"].unique())
unique_RHF = sorted(df_folketall["RHF"].unique())

enum_enhet = {v: k for k, v in enumerate(unique_enhet)}
enum_HF = {v: k for k, v in enumerate(unique_HF)}
enum_RHF = {v: k for k, v in enumerate(unique_RHF)}

per_person_mann = 0.007126
per_person_kvinne = 0.0056

kvinner_kreftformer = {'Bryst': 0.222,
                       'Lunge, luftrør': 0.101,
                       'Tykktarm': 0.098,
                       'Hud eksl. melanom': 0.075,
                       'Melanom i hud': 0.069,
                       'Livmorlegeme': 0.047,
                       'Leukemi': 0.036,
                       'Sentralnervesystemet': 0.033,
                       'Endetarm': 0.033,
                       'Eggstokk, eggleder m.m.': 0.031,
                       'Øvrige lokalisasjoner': 0.254}

menn_kreftformer = {'Prostata': 0.265,
                    'Lunge, luftrør': 0.09,
                    'Tykktarm': 0.078,
                    'Hud eksl. melanom': 0.077,
                    'Urinveier (eksl. nyre)': 0.07,
                    'Melanom i hud': 0.063,
                    'Endetarm': 0.043,
                    'Leukemi': 0.04,
                    'Nyre eksl. nyrebekken': 0.032,
                    'Non-Hodkin lymfom': 0.031,
                    'Øvrige lokalisasjoner': 0.211}

for k, v in kvinner_kreftformer.items():
    df_folketall[f'Kvinne {k}'] = df_folketall['Befolkning2020'] * v * per_person_kvinne


for k, v in menn_kreftformer.items():
    df_folketall[f'Mann {k}'] = df_folketall['Befolkning2020'] * v * per_person_mann

df_folketall["RHFnummer"] = df_folketall["RHF"].map(enum_RHF)
df_folketall["HFnummer"] = df_folketall["HF"].map(enum_HF)
df_folketall["enhet_nummer"] = df_folketall["Stråleterapienhet"].map(enum_enhet)

krefttype = "Mann Prostata"


kart_kommuner_file = open("norskeKommunerMedHelseinfoSomTall.json")
kart_kommuner = json.load(kart_kommuner_file)
kart_fylker_file = open("norskeKommunerBareFylker.json")
kart_fylker = json.load(kart_fylker_file)
kart_enheter_file = open("norskeKommunerBareEnheter.json")
kart_enheter = json.load(kart_enheter_file)
kart_HF_file = open("norskeKommunerBareHF.json")
kart_HF = json.load(kart_HF_file)
kart_RHF_file = open("norskeKommunerBareRHF.json")
kart_RHF = json.load(kart_RHF_file)

switch = "kommune"

kart = {"RHF": kart_RHF, "HF": kart_HF, "enhet": kart_enheter, "fylke": kart_fylker, "kommune": kart_kommuner}
kolonnenavn = {"RHF": "RHFnummer", "HF": "HFnummer", "enhet": "enhet_nummer", "fylke": "Fylkenr", "kommune": "Kommunenr"}
json_navn = {"RHF": "RHF", "HF": "HF", "enhet": "enhet", "fylke": "fylke", "kommune": "kommunenummer"}

hovertemplate = f"<i>Tilfeller {krefttype}</i><br>"

if switch == "kommune":
    dff = df_folketall.groupby(kolonnenavn[switch]).sum()
    customdata = np.stack(([get_kommune_from_nr(k) for k in dff.index], dff[krefttype], [get_fylke_from_kommunenr(k) for k in dff.index],
                           [get_HF_from_kommunenr(k) for k in dff.index],
                           [get_RHF_from_kommunenr(k) for k in dff.index],
                           [get_enhet_From_kommunenr(k) for k in dff.index]), axis=-1)
    hovertemplate += "<b>Fylke:</b>: %{customdata[2]}<br><b>Kommune:</b> %{customdata[0]}<br><b>Helseforetak:</b> %{customdata[3]}<br>"
    hovertemplate += "<b>Regionalt helseforetak:</b> %{customdata[4]}<br><b>Stråleterapienhet:</b> %{customdata[5]}<br>"
    hovertemplate += "<b>Krefttilfeller:</b> %{customdata[1]:.0f}<br><extra></extra>"

elif switch == "HF":
    dff = df_folketall.groupby(kolonnenavn[switch]).sum()
    customdata = np.stack((dff[krefttype], [unique_HF[k] for k in dff.index], [get_RHF(unique_HF[k]) for k in dff.index]), axis=-1)
    hovertemplate += "<b>Helseforetak:</b> %{customdata[1]}<br>"
    hovertemplate += "<b>Regionalt helseforetak:</b> %{customdata[2]}<br>"
    hovertemplate += "<b>Krefttilfeller:</b> %{customdata[0]:.0f}<br><extra></extra>"

elif switch == "RHF":
    dff = df_folketall.groupby(kolonnenavn[switch]).sum()
    customdata = np.stack((dff[krefttype], [unique_RHF[k] for k in dff.index]), axis=-1)
    hovertemplate += "<b>Regionalt helseforetak:</b> %{customdata[1]}<br>"
    hovertemplate += "<b>Krefttilfeller:</b> %{customdata[0]:.0f}<br><extra></extra>"

elif switch == "enhet":
    dff = df_folketall.groupby(kolonnenavn[switch]).sum()
    customdata = np.stack((dff[krefttype], [unique_enhet[k] for k in dff.index]), axis=-1)
    hovertemplate += "<b>Stråleterapienhet:</b> %{customdata[1]}<br>"
    hovertemplate += "<b>Krefttilfeller:</b> %{customdata[0]:.0f}<br><extra></extra>"

elif switch == "fylke":
    dff = df_folketall.groupby(kolonnenavn[switch]).sum()
    customdata = np.stack((dff[krefttype], [fylkenavn[k] for k in dff.index]), axis=-1)
    hovertemplate += "<b>Fylke:</b> %{customdata[1]}<br>"
    hovertemplate += "<b>Krefttilfeller:</b> %{customdata[0]:.0f}<br><extra></extra>"


dff = df_folketall.groupby(kolonnenavn[switch]).sum()

fig = go.Figure(go.Choroplethmapbox(geojson=kart[switch],
                                    locations=dff.index,
                                    z=np.log10(dff[krefttype]),
                                    featureidkey=f'properties.{json_navn[switch]}',
                                    colorscale='Viridis',
                                    customdata=customdata,
                                    hovertemplate=hovertemplate,
                                    colorbar=colorbar(1, 10000, 5)
                                    ))

fig.update_layout(mapbox_style="carto-positron",
                  mapbox_center={'lat': 65.5, 'lon': 16.463},
                  mapbox_zoom=4,)
fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
fig.show()
