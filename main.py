import tweepy
import os

# Solo se necesita el Bearer Token en el plan Free
BEARER_TOKEN = os.getenv("AAAAAAAAAAAAAAAAAAAAAOBt3gEAAAAAaVontg%2FKMnkRjiPL03yPm8sNidw%3D26GuqBbnSqLgS4poaI58wGmNc6TpKsXrgPRfWfMRrhK3dOcyHr")

client = tweepy.Client(bearer_token=BEARER_TOKEN)

query = "python"

try:
    response = client.search_recent_tweets(query=query, max_results=10)
    if response.data:
        for tweet in response.data:
            print(tweet.text)
    else:
        print("No se encontraron tweets.")
except Exception as e:
    print("Error:", e)
