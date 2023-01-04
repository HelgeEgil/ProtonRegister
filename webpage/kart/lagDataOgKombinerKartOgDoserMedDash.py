import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import json
import numpy as np
import os
from dash import Dash, dcc, html, Input, Output, ctx
import dash_bootstrap_components as dbc
import random


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


def get_bergenoslo_from_number(nr):
    if nr == 0:
        return "Bergen"
    else:
        return "Oslo"


def get_hovertemplate_customdata(switch, df_folketall, krefttype):
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

    elif switch == "bergenoslo":
        dff = df_folketall.groupby(kolonnenavn[switch]).sum()
        customdata = np.stack((dff[krefttype], [unique_BO[k] for k in dff.index]), axis=-1)
        hovertemplate += "<b>Behandlende senter:</b> %{customdata[1]}<br>"
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

    return hovertemplate, customdata


def get_highlights(selections, geojson, district_lookup):
    geojson_highlights = dict()
    for k in geojson.keys():
        if k != 'features':
            geojson_highlights[k] = geojson[k]
        else:
            geojson_highlights[k] = [district_lookup[selection] for selection in selections]
    return geojson_highlights


selection = set()

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

fylkenavn = {30: "Viken", 3: "Oslo", 34: "Innlandet", 54: "Troms og Finnmark", 18: "Nordland", 46: "Vestland", 11: "Rogaland",
             15: "Møre og Romsdal", 50: "Trøndelag", 38: "Vestfold og Telemark", 42: "Agder"}

df_folketall = pd.read_csv("kommuner.csv", header=0, sep=",")
unique_enhet = sorted(df_folketall["Stråleterapienhet"].unique())
unique_HF = sorted(df_folketall["HF"].unique())
unique_RHF = sorted(df_folketall["RHF"].unique())
unique_BO = ["Bergen", "Oslo"]

enum_enhet = {v: k for k, v in enumerate(unique_enhet)}
enum_HF = {v: k for k, v in enumerate(unique_HF)}
enum_RHF = {v: k for k, v in enumerate(unique_RHF)}

per_person_mann = 0.007126
per_person_kvinne = 0.0056

for k, v in kvinner_kreftformer.items():
    df_folketall[f'Kvinne {k}'] = df_folketall['Befolkning2020'] * v * per_person_kvinne

for k, v in menn_kreftformer.items():
    df_folketall[f'Mann {k}'] = df_folketall['Befolkning2020'] * v * per_person_mann

df_folketall["RHFnummer"] = df_folketall["RHF"].map(enum_RHF)
df_folketall["HFnummer"] = df_folketall["HF"].map(enum_HF)
df_folketall["enhet_nummer"] = df_folketall["Stråleterapienhet"].map(enum_enhet)
df_folketall["Bias D10"] = np.random.uniform(-5, 5, size=len(df_folketall))
df_folketall["bergenoslo"] = 1
df_folketall.loc[df_folketall.RHF == "Helse Vest", "bergenoslo"] = 0
df_folketall.loc[df_folketall.RHF == "Helse Nord", "bergenoslo"] = 0

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
kart_BO_file = open("norskeKommunerBareBergenOslo.json")
kart_BO = json.load(kart_BO_file)

switch = "HF"

kart = {"RHF": kart_RHF, "HF": kart_HF, "enhet": kart_enheter, "fylke": kart_fylker, "kommune": kart_kommuner, "bergenoslo": kart_BO}
kolonnenavn = {"RHF": "RHFnummer", "HF": "HFnummer", "enhet": "enhet_nummer", "fylke": "Fylkenr", "kommune": "Kommunenr", "bergenoslo": "bergenoslo"}
json_navn = {"RHF": "RHF", "HF": "HF", "enhet": "enhet", "fylke": "fylke", "kommune": "kommunenummer", "bergenoslo": "bergenoslo"}

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

strukturer = ["Lung_R", "Lung_L", "CTV", "stomach", "bowel"]

app.layout = html.Div([
    dbc.Row([
        dbc.Col([
            html.H3("Krefttilfeller per region"),
            html.Br(),
            html.P("Velg kjønn: "),
            dcc.RadioItems(id="sex", options=["Mann", "Kvinne"], value="Mann", inline=True, inputStyle={"margin-left": "20px"}),
            html.Br(),
            html.P("Velg krefttype: "),
            dcc.Dropdown(list(menn_kreftformer.keys()), list(menn_kreftformer.keys())[0], id="krefttype"),
            html.Br(),
            html.P("Velg kartinndeling: "),
            dcc.RadioItems(id="mapType",
                           options=[{'label': "Kommune", 'value': "kommune"},
                                    {'label': 'Fylke', 'value': 'fylke'},
                                    {'label': 'Helseforetak', 'value': 'HF'},
                                    {'label': 'Regionalt Helseforetak', 'value': 'RHF'}, {'label': 'Stråleterapienhet', 'value': 'enhet'},
                                    {'label': 'Bergen vs Oslo', 'value': 'bergenoslo'}],
                           value="kommune", inline=True, inputStyle={"margin-left": "20px"}),
            html.Br(),
            # dcc.Input(id="selection_result", type="text", placeholder=""),
            html.Div([dcc.Graph(id="map")], id="map_container"),
            html.P("Velg regioner for å vise mer informasjon til høyre.")
        ],
        ),

        dbc.Col(
            [
                html.H3("Parametere for valgte regioner"),
                html.Br(),
                html.P("Velg parameter: "),
                dcc.RadioItems(id="doseparameter", options=["D10%", "D50%", "D98%", "Volum"], value="D10%", inline=True, inputStyle={"margin-left": "20px"}),
                html.Br(),
                html.P("Velg strukturer: "),
                dcc.Checklist(strukturer, [strukturer[0]], id="strukturer", inline=True, inputStyle={"margin-left": "20px"}),
                html.Br(),
                dcc.Graph(id="dose")
            ],
        ),
    ],
        justify="center"
    ),
],
    style={"font-family": "Arial", "font-size": "0.9em", "text-align": "center"},
)


@app.callback(Output("map", "clickData"), [Input("map_container", "n_clicks")])
def reset_clickData(n_clicks):
    selection.clear()
    return None


@app.callback([Output('krefttype', 'options'), Output('krefttype', 'value')], Input('sex', 'value'))
def krefttype_options(sex_value):
    if sex_value == "Mann":
        options = [{'label': k, 'value': k} for k in menn_kreftformer.keys()]
        value = list(menn_kreftformer.keys())[0]
    else:
        options = [{'label': k, 'value': k} for k in kvinner_kreftformer.keys()]
        value = list(kvinner_kreftformer.keys())[0]

    return options, value


@app.callback(Output("map", "figure"), [Input("sex", "value"), Input("krefttype", "value"), Input("mapType", "value")])
def display_choropleth(sex, krefttype, mapType):
    sex_krefttype = f"{sex} {krefttype}"
    hovertemplate, customdata = get_hovertemplate_customdata(mapType, df_folketall, sex_krefttype)
    district_lookup = {feature['properties'][json_navn[mapType]]: feature for feature in kart[mapType]['features']}

    dff = df_folketall.groupby(kolonnenavn[mapType]).sum()

    fig = go.Figure(go.Choroplethmapbox(geojson=kart[mapType],
                                        locations=dff.index,
                                        z=np.log10(dff[sex_krefttype]),
                                        featureidkey=f'properties.{json_navn[mapType]}',
                                        colorscale='Viridis',
                                        customdata=customdata,
                                        hovertemplate=hovertemplate,
                                        colorbar=colorbar(1, 10000, 5)
                                        ))

    fig.update_layout(mapbox_style="open-street-map",
                      mapbox_center={'lat': 65.5, 'lon': 16.463},
                      mapbox_zoom=4)
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0}, autosize=False, width=800, height=800)
    return fig


@app.callback(Output("dose", "figure"),
              [Input("mapType", "value"), Input("sex", "value"), Input("krefttype", "value"),
               Input("doseparameter", "value"), Input("strukturer", "value"), Input("map", "clickData")])
def display_dose(mapType, sex, krefttype, doseparameter, strukturer, clickData):
    sex_krefttype = f"{sex} {krefttype}"

    # Dose RNG parameters, fix to set a bit more logically based on Dxx and structure

    mean_D10 = 20
    std_D10 = 5

    if clickData is not None:
        location = clickData['points'][0]['location']
        if location not in selection:
            selection.add(location)
        else:
            selection.remove(location)

    if mapType == "kommune":
        dict_pasient = {'kommune': list(), 'Dose': list()}
        for k in list(selection):
            navn = get_kommune_from_nr(k)
            dff = df_folketall.query(f'Kommunenavn == "{navn}"')

            bias = dff["Bias D10"].values[0]
            n = int(dff[sex_krefttype].sum())
            dict_pasient['kommune'] += [navn] * n
            dict_pasient['Dose'] += list(np.random.normal(mean_D10 + bias, std_D10, n))

    elif mapType == "HF":
        selection_list = [unique_HF[k] for k in list(selection)]
        selection_kommuner = {hf: list(df_folketall.query(f'HF == "{hf}"')["Kommunenavn"]) for hf in selection_list}
        dict_pasient = {'kommune': list(), 'HF': list(), 'Dose': list()}

        for hf, kommuner in selection_kommuner.items():
            for k in kommuner:
                dff = df_folketall.query(f'Kommunenavn == "{k}"')

                bias = dff["Bias D10"].values[0]
                n = int(dff[sex_krefttype].sum())
                dict_pasient['kommune'] += [k] * n
                dict_pasient['HF'] += [hf] * n
                dict_pasient['Dose'] += list(np.random.normal(mean_D10 + bias, std_D10, n))

    elif mapType == "RHF":
        selection_list = [unique_RHF[k] for k in list(selection)]
        selection_kommuner = {thisUnit: list(df_folketall.query(f'RHF == "{thisUnit}"')["Kommunenavn"]) for thisUnit in selection_list}
        dict_pasient = {'kommune': list(), 'RHF': list(), 'Dose': list()}

        for thisUnit, kommuner in selection_kommuner.items():
            for k in kommuner:
                dff = df_folketall.query(f'Kommunenavn == "{k}"')

                bias = dff["Bias D10"].values[0]
                n = int(dff[sex_krefttype].sum())
                dict_pasient['kommune'] += [k] * n
                dict_pasient['RHF'] += [thisUnit] * n
                dict_pasient['Dose'] += list(np.random.normal(mean_D10 + bias, std_D10, n))

    elif mapType == "enhet":
        selection_list = [unique_enhet[k] for k in list(selection)]
        selection_kommuner = {thisUnit: list(df_folketall.query(f'Stråleterapienhet == "{thisUnit}"')["Kommunenavn"]) for thisUnit in selection_list}
        dict_pasient = {'kommune': list(), 'enhet': list(), 'Dose': list()}

        for thisUnit, kommuner in selection_kommuner.items():
            for k in kommuner:
                dff = df_folketall.query(f'Kommunenavn == "{k}"')

                bias = dff["Bias D10"].values[0]
                n = int(dff[sex_krefttype].sum())
                dict_pasient['kommune'] += [k] * n
                dict_pasient['enhet'] += [thisUnit] * n
                dict_pasient['Dose'] += list(np.random.normal(mean_D10 + bias, std_D10, n))

    elif mapType == "bergenoslo":
        selection_list = [unique_BO[k] for k in list(selection)]
        selection_kommuner = {thisUnit: list(df_folketall.query(f'bergenoslo == "{thisUnit}"')["Kommunenavn"]) for thisUnit in list(selection)}
        dict_pasient = {'kommune': list(), 'bergenoslo': list(), 'Dose': list()}

        for thisUnit, kommuner in selection_kommuner.items():
            for k in kommuner:
                dff = df_folketall.query(f'Kommunenavn == "{k}"')
                thisName = thisUnit == 0 and "Bergen" or "Oslo"

                bias = dff["Bias D10"].values[0]
                n = int(dff[sex_krefttype].sum())
                dict_pasient['kommune'] += [k] * n
                dict_pasient['bergenoslo'] += [thisName] * n
                dict_pasient['Dose'] += list(np.random.normal(mean_D10 + bias, std_D10, n))

    df_pasient = pd.DataFrame(dict_pasient)

    fig = px.histogram(df_pasient, x="Dose", color=mapType, opacity=0.7, barmode="overlay", labels={"bergenoslo": "Behandlende senter"})

    fig.update_layout(yaxis_title="Antall pasienter", xaxis_title=f"{doseparameter} [Gy]")

    return fig


"""
@app.callback(Output("selection_result", "value"), [Input("map", "clickData")])
def store_data(clickData):
    if clickData is None:
        return ""
    else:
        location = clickData['points'][0]['location']

        if location not in selection:
            selection.add(location)
        else:
            selection.remove(location)

"""
app.run_server(debug=True)
