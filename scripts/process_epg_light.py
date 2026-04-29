import requests
from unidecode import unidecode
import xml.etree.ElementTree as ET
import gzip
import shutil
import sys
import re
import os

def transliterate(text):
    if text is None:
        return None

    if not text.strip():
        return text

    chr_live = False
    if text.find("⋗") != -1:
        text = text.replace("⋗", "")
        chr_live = True

    text = unidecode(text)

    if chr_live:
        text = "⋗ " + text

    return text

# Estrai canali da m3u ---
m3u_channels = set()
m3u_list = "docs/m3u"

if not os.path.exists(m3u_list):
    print(f"File m3u non trovato: {m3u_list}")
    sys.exit(1)

with open(m3u_list, "r", encoding="utf-8") as m3u:
    for line in m3u:
        if line.startswith("#EXTINF"):
            tvg_id_match = re.search(r'tvg-id="([^"]+)"', line)
            if tvg_id_match:
                tvg_id = tvg_id_match.group(1)
                m3u_channels.add(tvg_id)

if not m3u_channels:
    print("Nessun canale trovato in m3u. Assicurati che il file sia corretto.")
    sys.exit(1)
# --- Fine estrazione canali m3u ---

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

# Rimuovi i canali non presenti in m3u
for channel in list(root.findall("channel")):
    if channel.attrib.get("id") not in m3u_channels:
        root.remove(channel)

# Rimuovi i programmi non presenti in m3u
for programme in list(root.findall("programme")):
    if programme.attrib.get("channel") not in m3u_channels:
        root.remove(programme)

# Translitera testi cirillici in ASCII
for elem in root.iter():
    if elem.text and any("\u0400" <= c <= "\u04FF" for c in elem.text):
        elem.text = transliterate(elem.text)

# Salva l'XML modificato
tree.write("docs/epg_light.xml", encoding="utf-8", xml_declaration=True)
