from flask import Flask, redirect, url_for, render_template, request, session
from dotenv import load_dotenv
import tweepy 
import config
import os
import hashlib
import requests
import secrets
import base64
import openai

load_dotenv()

client_id = os.getenv('TWITTER_CLIENT_ID')
client_secret = os.getenv('TWITTER_CLIENT_SECRET')
redirect_uri = os.getenv("TWITTER_CALLBACK_URI")

app = Flask(__name__)

app.secret_key = os.urandom(24)

#Twitter endpoints for 0Auth2
authorize_url = "https://twitter.com/i/oauth2/authorize"
token_url = "https://api.twitter.com/2/oauth2/token"
user_info_url = "https://api.twitter.com/2/users/me"

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
    state = request.args.get("state")
    code_verifier = session.get("code_verifier")

    token_data = {
        "client_id": client_id,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
        "code_verifier": code_verifier
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    token_response = requests.post(token_url, data=token_data, headers=headers)
    token_json = token_response.json()

    session['access_token'] = token_json['access_token']
    session['refresh_token'] = token_json.get('refresh_token')

    headers = {
        "Authorization": f"Bearer {session['access_token']}"
    }

    user_info_response = requests.get(user_info_url, headers=headers)
    user_info = user_info_response.json()

    timeline_data = fetch_reverse_chronological_timeline(session['access_token'], user_info['data']['id'])

    if timeline_data:
        tweets=[tweet['text'] for tweet in timeline_data['data']]
        return f"Recent Tweets:<br>" + "<br>".join(tweets)
    else:
        return "Failed to fetch home timeline"

def code_verification():
    code_verifier = secrets.token_urlsafe(128)
    return code_verifier

def code_challenger(code_verifier):
    code_challenge = base64.urlsafe_b64encode(hashlib.sha256(code_verifier.encode()).digest()).rstrip(b'=').decode('utf-8')
    return code_challenge

def fetch_reverse_chronological_timeline(access_token, user_id):
    url = f"https://api.twitter.com/2/users/{user_id}/timelines/reverse_chronological"

    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    params = {
        "max_results": 10,
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        print(f"Response Header: {response.headers}")
        print(f"Response Body: {response.text}")
        return None
    
def summarize_tweets(tweets):
    tweets_text = " ".join(tweets)
    model = "gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are designed to drill down to the context of tweets, summarise the topics under discussion and present it to the end user as summaries"},
        {"role": "user", "content": f"drill down to the context of the following tweets, summarise the topics under discussion and present it to the end user as summaries"}]
    
    summary = response['choices'][0]['message']['content'].strip()
    return summary.split('\n')

if __name__ == "__main__":
    app.run(debug=True)
