import tweepy
import os

# Solo se necesita el Bearer Token en el plan Free
BEARER_TOKEN = os.getenv("AAAAAAAAAAAAAAAAAAAAAOBt3gEAAAAAnc149k6%2Bwr2iN%2FtU003xFTBq4EE%3DIE2bAWyaInOw8FjvFWdNxOGp35plpsypFHr3htA0wVjejUMLi2")

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
