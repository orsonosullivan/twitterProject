import tweepy 
import config
import pandas as pd

client = tweepy.Client(bearer_token=config.BEARER_TOKEN)

query = 'dublin'

response = client.search_recent_tweets(query=query, max_results=10)

columns = ['ID', 'Text']
data = []
for tweet in response:
    data.append(tweet)

print(response)