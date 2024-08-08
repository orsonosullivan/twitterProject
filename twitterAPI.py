import tweepy
import configparser

#read configs 
config = configparser.ConfigParser()
config.read('config.ini')

api_key = config['twitter']['api_key']
api_key_secret = config['twitter']['api_secret_key']
access_token = config['twitter']['access_token']
access_token_secret = config['twitter']['access_token_secret']
bearer_token = config['twitter']['bearer_token']

#authentication 
client = tweepy.Client(bearer_token)
print(bearer_token)