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
m3u_list = "docs/playlist.m3u"

print("Estrazione canali da m3u...")
if not os.path.exists(m3u_list):
    print(f"File m3u non trovato: {m3u_list}")
    sys.exit(1)

print(f"Analizzando il file m3u: {m3u_list}")
with open(m3u_list, "r", encoding="utf-8") as m3u:
    for line in m3u:
        if line.startswith("#EXTINF"):
            tvg_id_match = re.search(r'tvg-id="([^"]+)"', line)
            if tvg_id_match:
                tvg_id = tvg_id_match.group(1)
                m3u_channels.add(tvg_id)

print(f"Canali trovati in m3u: {len(m3u_channels) + 1}")
if not m3u_channels:
    print("Nessun canale trovato in m3u. Assicurati che il file sia corretto.")
    sys.exit(1)    
# --- Fine estrazione canali m3u ---

# URL dell'EPG XMLTV originale
URL_EPG = "https://iptvx.one/EPG_NOARCH"

print("Inizio processo di download e processamento dell'EPG...")
response = requests.get(URL_EPG)
with open("epg.xml.gz", "wb") as f:
    f.write(response.content)

print("EPG scaricato con successo. Decompressione in corso...")
with gzip.open("epg.xml.gz", "rb") as f_in:
    with open("epg.xml", "wb") as f_out:
        shutil.copyfileobj(f_in, f_out)

print("EPG scaricato e decompresso con successo.")
tree = ET.parse("epg.xml")
root = tree.getroot()

print("Rimozione canali non presenti in m3u...")
for channel in list(root.findall("channel")):
    if channel.attrib.get("id") not in m3u_channels:
        root.remove(channel)

print("Rimozione programmi non presenti in m3u...")
for programme in list(root.findall("programme")):
    if programme.attrib.get("channel") not in m3u_channels:
        root.remove(programme)

print("Transliterazione testi cirillici...")
for elem in root.iter():
    if elem.text and any("\u0400" <= c <= "\u04FF" for c in elem.text):
        elem.text = transliterate(elem.text)

print("Processamento completato. Salvataggio del file XML...")
tree.write("docs/epg.xml", encoding="utf-8", xml_declaration=True)

print("File EPG processato e salvato in docs/epg.xml")
deleted_files = ["epg.xml", "epg.xml.gz"]
for file in deleted_files:
    if os.path.exists(file):
        os.remove(file)
        print(f"File temporaneo eliminato: {file}")
    else:
        print(f"File temporaneo non trovato (già eliminato?): {file}")
        