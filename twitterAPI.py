import tweepy 
import config

client = tweepy.Client(bearer_token=config.BEARER_TOKEN)

query = 'dublin'

response = client.search_recent_tweets(query=query, max_results=10)

tweet_texts = [tweet.text for tweet in response.data]

print(tweet_texts)
