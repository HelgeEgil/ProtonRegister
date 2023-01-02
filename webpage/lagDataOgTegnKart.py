import pandas as pd
import plotly.graph_objects as go
import json
import numpy as np

def colorbar(zmin, zmax, n = 6):
    return dict(
        title = "Krefttilfeller",
        tickmode = "array",
        tickvals = np.linspace(np.log10(zmin), np.log10(zmax), n),
        ticktext = np.round(10 ** np.linspace(np.log10(zmin), np.log10(zmax), n), 1)
    )

df_folketall = pd.read_csv("folketall_rensket.csv", header=0, sep=";")

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
                    
for k,v in kvinner_kreftformer.items():
    df_folketall[f'Kvinne {k}'] = df_folketall['Antall'] * v * per_person_kvinne


for k,v in menn_kreftformer.items():
    df_folketall[f'Mann {k}'] = df_folketall['Antall'] * v * per_person_mann

kommuner_file = open("norskeKommuner.json")
kommuner = json.load(kommuner_file)
krefttype = "Mann Prostata"

customdata = np.stack((df_folketall['Kommunenavn'], df_folketall[krefttype]), axis=-1)
hovertemplate = f"<i>Tilfeller {krefttype}</i><br>" + \
                "<b>Kommune:</b> %{customdata[0]}<br>" +\
                "<b>Krefttilfeller:</b> %{customdata[1]:.0f}<br>"


fig = go.Figure(go.Choroplethmapbox(geojson=kommuner,
                                    locations=df_folketall["Kommunenr"],
                                    z=np.log10(df_folketall[krefttype]),
                                    featureidkey='properties.kommunenummer',
                                    colorscale='Viridis',
                                    customdata=customdata,
                                    hovertemplate = hovertemplate,
                                    colorbar = colorbar(1, 10000, 5)
                                    ))


fig.update_layout(mapbox_style="carto-positron",
                  mapbox_center = {'lat': 65.5, 'lon': 16.463},
                  mapbox_zoom = 4,)
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
fig.show()
