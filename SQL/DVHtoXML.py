import numpy as np
from dicttoxml import dicttoxml


def arrayToXML(array, fieldname):
    """Generates an XML Typed array."""
    string = '<?xml version="1.0" encoding="utf-8"?><resources><array name="DoseGy">'
    for a in array:
        string += f"<item>{a:.4f}</item>"
    string += '</array></resources>'
    return string


x = np.linspace(0, 10, 1000)
y = np.linspace(10, 5, 1000)

doseArrayXML = arrayToXML(x, "DoseGy")
volumeArrayXML = arrayToXML(y, "VolumePercent")

print(doseArrayXML)
print(len(doseArrayXML))
# Length of field should be 25000 (up to 131 Gray)