from flask import Flask, redirect, url_for, render_template, request, session
#from authlib.integration.flask_client import OAuth
from dotenv import load_dotenv
import tweepy 
import config
import os
import hashlib
import requests

load_dotenv()

client_id = os.getenv('TWITTER_CLIENT_ID')
client_secret = os.getenv('TWITTER_CLIENT_SECRET')
redirect_uri = os.getenv("TWITTER_CALLBACK_URL")


app = Flask(__name__)

#Twitter endpoints for 0Auth2
authorize_url = "https://twitter.com/i/oauth2/authorize"
token_url = "https://api.twitter.com/2/oauth2/token"
user_info_url = "https://api.x.com/2/me"


#From auth0 docs:
def code_verification():
    code_verification = secrets.token_urlsafe(128)
    return code_verifier

#From authO docs: create code challenge: Generate a code_challenge from the code_verifier that will be sent to Auth0 to request an authorization_code
def code_challenger():
    code_challenger = base64.urlsafe_b64encode(hashlib.sha256(code_verifier.encode()).digest()).rstrip(b'=').decode('utf-8')
    return code_challenge

#search function using tweepy 
def process_query(query):
    client = tweepy.Client(bearer_token=config.BEARER_TOKEN)
    response = client.search_recent_tweets(query=query, max_results=10)
    tweet_texts = [tweet.text for tweet in response.data]
    tweet_texts = str_replace_all(tweets_list, "[\r\n]" , "")

    print (tweet_texts)
    return f"Processed tweets: {tweet_texts}"

#login page
@app.route('/login')
def login():
    return twitter.authorize_redirect(redirect_uri=app.config["TWITTER_CALLBACK_URL"])


#landing page 
@app.route("/")
def home():
    code_verifier = generate_code_verifier()
    code_challenge = generate_code_challenge(code_verifier)

    return render_template("welcomepage.html")

#search function
@app.route('/search', methods=['POST'])
def search():
    query = request.form['query']
    result = process_query(query)
    return render_template('resultpage.html', query=query,result=result)

if __name__ == "__main__":
    app.run()
