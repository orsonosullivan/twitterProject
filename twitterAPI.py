import tweepy
import configparser

#read configs 
config = configparser.ConfigParser()
config.read('config.ini')

api_key = config['twitter']['api_key']
api_key_secret = config['twitter']['api_secret_key']

access_token = config['twitter']['client_id']
access_token_secret = config['twitter']['client_id_secret']

print(api_key)
 