import os
import time
import random
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import tweepy
import schedule
from flask import Flask

# =============================
# 🔑 Autenticación con Twitter
# =============================
load_dotenv()

API_KEY = os.getenv("API_KEY")
API_SECRET_KEY = os.getenv("API_SECRET_KEY")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")
BEARER_TOKEN = os.getenv("BEARER_TOKEN")

client = tweepy.Client(
    bearer_token=BEARER_TOKEN,
    consumer_key=API_KEY,
    consumer_secret=API_SECRET_KEY,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET
)

user = client.get_me()
print(f"✅ Autenticado como: {user.data.username}")

# =============================
# 🎯 Hashtags
# =============================
HASHTAGS = {
    "clima": ["#Clima", "#MarDelPlata", "#Argentina", "#Tiempo"],
    "dolar": ["#Dólar", "#Economía", "#Argentina", "#Finanzas"],
    "noticia": ["#Noticias", "#Argentina", "#Actualidad", "#Info"]
}

def elegir_hashtags(tipo):
    return " ".join(random.sample(HASHTAGS[tipo], 2))

# =============================
# 🌦 Funciones
# =============================
def get_clima():
    url = "https://wttr.in/Mar+del+Plata?format=3"
    try:
        clima = requests.get(url).text.strip()
        return clima
    except:
        return "No se pudo obtener el clima."

def get_dolar():
    url = "https://dolarhoy.com/"
    try:
        resp = requests.get(url).text
        soup = BeautifulSoup(resp, "html.parser")
        compra = soup.find("div", {"class": "val"}).text
        venta = soup.find_all("div", {"class": "val"})[1].text
        return f"Dólar hoy: Compra {compra} | Venta {venta}"
    except:
        return "No se pudo obtener la cotización del dólar."

def get_noticia():
    url = "https://www.lanacion.com.ar/ultimas-noticias/"
    try:
        resp = requests.get(url).text
        soup = BeautifulSoup(resp, "html.parser")
        titulo = soup.find("h2").text.strip()
        return f"📰 {titulo}"
    except:
        return "No se pudo obtener la noticia."

# =============================
# 🐦 Tuits automáticos
# =============================
def post_clima():
    texto = get_clima()
    tweet = f"{texto} {elegir_hashtags('clima')}"
    client.create_tweet(text=tweet)
    print(f"✅ Tweet Clima: {tweet}")

def post_dolar():
    texto = get_dolar()
    tweet = f"{texto} {elegir_hashtags('dolar')}"
    client.create_tweet(text=tweet)
    print(f"✅ Tweet Dólar: {tweet}")

def post_noticia():
    texto = get_noticia()
    tweet = f"{texto} {elegir_hashtags('noticia')}"
    client.create_tweet(text=tweet)
    print(f"✅ Tweet Noticia: {tweet}")

# =============================
# ⏰ Programación de tareas
# =============================
schedule.every(7).hours.do(post_clima)      # Clima cada 7 horas
schedule.every(3).hours.do(post_dolar)      # Dólar cada 3 horas
schedule.every(50).minutes.do(post_noticia) # Noticias cada 50 minutos

print("🤖 Bot iniciado. Esperando tareas...")

# =============================
# 🌍 Flask para mantener vivo
# =============================
app = Flask(__name__)

@app.route("/")
def home():
    return "🤖 Bot de Twitter corriendo!"

def run_scheduler():
    while True:
        schedule.run_pending()
        print("⏳ Esperando...")
        time.sleep(60)

if __name__ == "__main__":
    import threading
    threading.Thread(target=run_scheduler).start()
    app.run(host="0.0.0.0", port=5000)
if __name__ == "__main__":
    # Inicia el bot en segundo plano
    threading.Thread(target=ejecutar_bot, daemon=True).start()

    # Levanta un servidor Flask para mantener vivo el repl
    app.run(host="0.0.0.0", port=5000)
