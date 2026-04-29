import requests
from unidecode import unidecode
import xml.etree.ElementTree as ET
import gzip
import shutil
from datetime import datetime, timedelta

# URL dell'EPG XMLTV originale
URL_EPG = "https://iptvx.one/EPG_NOARCH"

# Scarica l'EPG compresso
response = requests.get(URL_EPG)
with open("epg.xml.gz", "wb") as f:
    f.write(response.content)

# Decomprimi il file
with gzip.open("epg.xml.gz", "rb") as f_in:
    with open("epg.xml", "wb") as f_out:
        shutil.copyfileobj(f_in, f_out)

# Carica l'XML
tree = ET.parse("epg.xml")
root = tree.getroot()

# Translitera testi cirillici in ASCII
for elem in root.iter():
    if elem.text and any("\u0400" <= c <= "\u04FF" for c in elem.text):
        elem.text = unidecode(elem.text.replace('⋗','.>'))
        elem.text = elem.text.replace('.>','⋗')

"""
# Aggiungi il timeshift di -0800
timeshift = timedelta(hours=-8)
for elem in root.iter("programme"):
    for attr in ["start", "stop"]:
        if attr in elem.attrib:
            original_time = elem.attrib[attr]
            # Converti il timestamp in datetime
            dt = datetime.strptime(original_time[:14], "%Y%m%d%H%M%S")
            # Applica il timeshift
            shifted_time = dt + timeshift
            # Aggiorna l'attributo con il nuovo timestamp e mantieni il formato originale
            elem.attrib[attr] = shifted_time.strftime("%Y%m%d%H%M%S") + original_time[14:]
"""

# Salva l'XML modificato
tree.write("epg_modified.xml", encoding="utf-8", xml_declaration=True)

# Comprimi nuovamente il file elaborato
with open("epg_modified.xml", "rb") as f_in:
    with gzip.open("docs/epg.xml.gz", "wb") as f_out:
        shutil.copyfileobj(f_in, f_out)
