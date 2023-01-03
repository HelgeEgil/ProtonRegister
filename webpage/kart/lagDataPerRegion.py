import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random

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

print(unique_HF)

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

df_folketall["Bias D10"] = np.random.uniform(-5, 5, size=len(df_folketall))

krefttype = "Mann Prostata"

hf1 = "Helse Bergen"
hf2 = "Helse Fonna"

hf_list = ["Helse Bergen", "Oslo Universitetssykehus", "Helgelandssykehuset"]

bias_D10 = {k: 8 * random.random() - 5 for k in unique_HF}
mean_D10 = 20
std_D10 = 5

hf_kommuner = { hf: list(df_folketall.query(f'HF == "{hf}"')["Kommunenavn"]) for hf in hf_list }

X = {hf: np.zeros((0)) for hf in hf_list }

for hf, kommuner in hf_kommuner.items():
    for k in kommuner:
        dff = df_folketall.query(f'Kommunenavn == "{k}"')
        bias = dff["Bias D10"].values[0]
        n = int(dff[krefttype].sum())
        X[hf] = np.concatenate((X[hf], np.random.normal(mean_D10 + bias, std_D10, n)))

hf_n = { hf: len(X[hf]) for hf in hf_list }

for hf, Xi in X.items():
    fig = plt.hist(Xi, bins=50, alpha=0.6, label=f"{hf} (N={hf_n[hf]})")
plt.title(f"Blæredose for {krefttype}")
plt.axvline(x=mean_D10, color="red", linestyle="--", label="Landsgjennomsnitt")
plt.xlabel("D10% til blære [Gy]")
plt.ylabel("Pasienter")
plt.legend()
plt.show()
