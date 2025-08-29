import tweepy
import os

# === Cargar claves desde variables de entorno ===
API_KEY = os.getenv("7uhvGASTQkWwE2BWHVN4iETNO")
API_KEY_SECRET = os.getenv("Wg9ggAZjwiCn4hv4HExd2kKBYyE16bMF4AKBqReTszhvn0gvtb")
ACCESS_TOKEN = os.getenv("1956489748622495744-BBqpYo75NYT5ksTRO8YWN6s966vZok")
ACCESS_TOKEN_SECRET = os.getenv("3K4i9odmt3l0p15QjL9hTMa8DBUzYSnvKtfJBiGcmCdtf")
BEARER_TOKEN = os.getenv("AAAAAAAAAAAAAAAAAAAAAOBt3gEAAAAAnc149k6%2Bwr2iN%2FtU003xFTBq4EE%3DIE2bAWyaInOw8FjvFWdNxOGp35plpsypFHr3htA0wVjejUMLi2")

# === Autenticación ===
client = tweepy.Client(
    bearer_token=BEARER_TOKEN,
    consumer_key=API_KEY,
    consumer_secret=API_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_SECRET
)

# === Palabra clave a buscar ===
KEYWORD = "VLLC"  # <-- cambia por la palabra que quieras

def buscar_y_retweet():
    # Buscar tweets recientes con la palabra
    tweets = client.search_recent_tweets(query=KEYWORD, max_results=10)
    if tweets.data:
        for t in tweets.data:
            try:
                client.retweet(t.id)
                print(f"Retuiteado: {t.text}")
            except Exception as e:
                print(f"Error con tweet {t.id}: {e}")

if __name__ == "__main__":
    buscar_y_retweet()
