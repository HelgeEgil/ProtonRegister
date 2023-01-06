from flask import Flask, render_template, request, redirect, Response

import json
import plotly
import plotly.express as px
import plotly.graph_objs as go
import pandas as pd

from gevent.pywsgi import WSGIServer
from gevent import monkey
from time import time

monkey.patch_all()

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib import pyplot as plt
from matplotlib.lines import Line2D
import base64
import pyodbc
import io

import numpy as np

RTPark = Flask(__name__)

def connection():
    conn = pyodbc.connect("Driver={SQL Server};SERVER={PC163196\SQLEXPRESS};database=testregister;")
    return conn


@RTPark.route("/")
def main_page():
    colorList = ['rgb(27,158,119)','rgb(217,95,2)','rgb(117,112,179)','rgb(231,41,138)','rgb(102,166,30)']

    dataPerStructure = {}
    patients = []
    patientNames = {}
    patientID = {}
    structureBasis = []
    labels = {}
    colorPicker = {}

    conn = connection()
    cursor = conn.cursor()
    cursor2 = conn.cursor()
    cursor.execute("SELECT * FROM dbo.RTImageSeries")
    for row in cursor.fetchall():
        cursor2.execute("SELECT StructureName FROM dbo.DVH WHERE RTImageSeriesID = ?", row.ID)
        rows = cursor2.fetchall()
        structures = ", ".join([k[0] for k in rows])
        patients.append({"modality": row.Modality, "PatientName": row.PatientName,
            "SeriesInstanceUID": row.SeriesInstanceUID, "ModelName": row.ManufacturersModelName,
             "Structures": structures, "kVp": row.kVp})
        patientNames[row.ID] = row.PatientName

    cursor.execute("SELECT PatientName FROM dbo.RTImageSeries WHERE id IN (SELECT RTImageSeriesID FROM dbo.DVH)")
    for row in cursor.fetchall():
        structureBasis.append(row[0])

    cursor = conn.cursor()
    cursor.execute("SELECT * from dbo.DVH")

    for row in cursor.fetchall():
        structureName = row.StructureName
        labels[structureName] = labels.get(structureName, 0) + 1
        patientName = patientNames[row.RTImageSeriesID]

        raw_dose_Gy = row.DVH_dose_Gy
        raw_volume_percent = row.DVH_volume_percent

        if not structureName in colorPicker:
            colorPicker[structureName] = colorList.pop()
        color = colorPicker[structureName]

        thisDose = [float(k) for k in raw_dose_Gy.split(",")]
        thisVolume = [float(k) for k in raw_volume_percent.split(",")]


        if not structureName in dataPerStructure:
            dataPerStructure[structureName] = dict()
        
        dataPerStructure[structureName][patientName] = { 'dose': thisDose, 'volume':thisVolume}

    # Make Plotly plot
    try:
        plot_builder = list()
        for structureName in dataPerStructure.keys():
            plotLegend = True
            for patientName, dataDict in dataPerStructure[structureName].items():
                plot_builder.append(go.Scatter(
                                        name=structureName,
                                        x=dataDict['dose'],
                                        y=dataDict['volume'],
                                        mode="lines",
                                        legendgroup=structureName,
                                        marker=dict(color=colorPicker[structureName], size=0.7),
                                        hovertemplate=f'Patient: {patientName}' + '<br>Dose: %{x:.1f} Gy' + '<br>Volume: %{y:.1f}%',
                                        showlegend=plotLegend))
                plotLegend = False

    except Exception as e:
        print(f"Plot error! {e}")


    fig = go.Figure(plot_builder)
    fig.update_layout(yaxis_title="Volume [%]", xaxis_title="Dose [Gy]")
    fig.update_layout(autosize=False, width=1000, height=600)

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)


    # Calculate median DVH values per structure
    """
    for structureName, dataDict in dataPerStructure.items():
        doses = dataDict['dose']
        volumes = dataDict['volume']

        maxLength, maxIdx = -1, -1
        for idx, dose in enumerate(doses):
            if len(dose) > maxLength:
                maxIdx = idx
                maxLength = len(dose)

        common_dose = doses[maxIdx]
        padded_volumes = np.zeros((len(doses), maxLength))
        for idx, volume in enumerate(volumes):
            l = len(volume)
            ll = maxLength - l
            padded_volumes[idx] = np.pad(volume, pad_width=(0, ll))

        median_volume = np.median(padded_volumes, axis=0)
        plt.plot(common_dose, median_volume, lw=3, c="k")
        plt.plot(common_dose, median_volume, lw=2.5, c=colorPicker[structureName])


    custom_lines = dict()
    for name, color in colorPicker.items():
        custom_lines[name] = Line2D([0], [0], color=color, lw=1.25)
    
    custom_lines[""] = Line2D([], [], ls='')
    custom_lines["Per patient"] = Line2D([0], [0], color="k", lw=0.7)
    custom_lines["Median"] = Line2D([0], [0], color="k", lw=2.5)

    plt.legend(custom_lines.values(), custom_lines.keys())


    conn.close()
    """
    return render_template("dist/indexPlotly.html", patients = patients, patientsWithStructures=structureBasis, graphJSON=graphJSON)

def main():
    http = WSGIServer(('', 5000), RTPark.wsgi_app)
    http.serve_forever()

if(__name__ == "__main__"):
    #RTPark.run(debug=True)
    main()