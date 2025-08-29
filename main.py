import snscrape.modules.twitter as sntwitter
import requests
import os

# ⚠️ Las claves las cargás en Render como Environment Variables
BUFFER_TOKEN = os.getenv("1956489748622495744-BBqpYo75NYT5ksTRO8YWN6s966vZok")
PROFILE_ID = os.getenv("Q3FWSjNoVGMwNUc5bHRjb0VkcEM6MTpjaQ")

# Palabra clave a buscar
PALABRA = "vllc"

def buscar_tuits(palabra, limite=3):
    """Busca tuits que contengan la palabra clave."""
    tuits = []
    for i, tweet in enumerate(sntwitter.TwitterSearchScraper(palabra).get_items()):
        if i >= limite:
            break
        tuits.append(tweet.content)
    return tuits

def publicar_en_buffer(texto):
    """Publica un texto en Buffer."""
    url = "https://api.bufferapp.com/1/updates/create.json"
    data = {
        "text": texto,
        "profile_ids[]": PROFILE_ID,
        "now": True
    }
    headers = {"Authorization": f"Bearer {BUFFER_TOKEN}"}
    res = requests.post(url, data=data, headers=headers)
    print("Respuesta Buffer:", res.json())

if _name_ == "_main_":
    print("🔍 Buscando tuits con la palabra:", PALABRA)
    tuits = buscar_tuits(PALABRA, limite=2)  # busca 2 tuits
    for tuit in tuits:
        print("Encontrado:", tuit[:80], "...")
        publicar_en_buffer(tuit)
