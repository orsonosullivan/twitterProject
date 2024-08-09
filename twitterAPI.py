from flask import Flask, redirect, url_for, render_template, request, session
#from authlib.integration.flask_client import OAuth
from dotenv import load_dotenv
import tweepy 
import config
import os
import hashlib
import requests
import secrets
import base64

load_dotenv()

client_id = os.getenv('TWITTER_CLIENT_ID')
client_secret = os.getenv('TWITTER_CLIENT_SECRET')
redirect_uri = os.getenv("TWITTER_CALLBACK_URI")

print(f"Client ID: {client_id}")
print(f"Client Secret: {client_secret}")  # Be cautious with printing secrets in production
print(f"Redirect URI: {redirect_uri}")


app = Flask(__name__)

app.secret_key = os.urandom(24)

#Twitter endpoints for 0Auth2
authorize_url = "https://twitter.com/i/oauth2/authorize"
token_url = "https://api.twitter.com/2/oauth2/token"
user_info_url = "https://api.twitter.com/2/users/me"

#login page
#@app.route('/login')
#def login():
#   return twitter.authorize_redirect(redirect_uri=app.config["TWITTER_CALLBACK_URL"])

#landing page 
@app.route("/")
def home():
    code_verifier = code_verification()
    code_challenge = code_challenger(code_verifier)
    session['code_verifier'] = code_verifier

    params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scope": "tweet.read users.read",
        "state": secrets.token_urlsafe(16),
        "code_challenge": code_challenge,
        "code_challenge_method": "S256"
    }

    url = requests.Request("GET", authorize_url, params=params).prepare().url
    print(url)
    return redirect(url)

@app.route("/callback")
def callback():
    code = request.args.get("code")
    code_verifier = session.get("code_verifier")

    if not code or not code_verifier:
        return "Error: Missing code or code_verifier", 400

    # Exchange the authorization code for an access token
    token_data = {
        "client_id": client_id,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
        "code_verifier": code_verifier
    }

    token_response = requests.post(token_url, data=token_data)
    token_json = token_response.json()
    print(token_response)

    if "access_token" not in token_json:
        return "Error: Could not obtain access token", 400

    access_token = token_json["access_token"]

    # Use the access token to fetch user info
    headers = {"Authorization": f"Bearer {access_token}"}
    user_info_response = requests.get(USER_INFO_URL, headers=headers)
    user_info = user_info_response.json()

    return f"Hello, {user_info['data']['name']}!"

#search function
@app.route('/search', methods=['POST'])
def search():
    query = request.form['query']
    result = process_query(query)
    return render_template('resultpage.html', query=query,result=result)

def code_verification():
    code_verifier = secrets.token_urlsafe(128)
    return code_verifier

#From authO docs: create code challenge: Generate a code_challenge from the code_verifier that will be sent to Auth0 to request an authorization_code
def code_challenger(code_verifier):
    code_challenge = base64.urlsafe_b64encode(hashlib.sha256(code_verifier.encode()).digest()).rstrip(b'=').decode('utf-8')
    return code_challenge

#search function using tweepy 
def process_query(query):
    client = tweepy.Client(token['access_token'])
    response = client.search_recent_tweets(query=query, max_results=10)
    tweet_texts = [tweet.text for tweet in response.data]
    tweet_texts = [tweet.replace("\r", "").replace("\n", "") for tweet in tweet_texts]

    print (tweet_texts)
    return f"Processed tweets: {tweet_texts}"

if __name__ == "__main__":
    app.run()
