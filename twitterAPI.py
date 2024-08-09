from flask import Flask, redirect, url_for, render_template, request, session
from dotenv import load_dotenv
import os
import hashlib
import requests
import secrets
import base64
from openai import OpenAI
import re

load_dotenv()

#getting env vars
client_id = os.getenv('TWITTER_CLIENT_ID')
client_secret = os.getenv('TWITTER_CLIENT_SECRET')
redirect_uri = os.getenv("TWITTER_CALLBACK_URI")
openai_api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)

app.secret_key = os.urandom(24)

#Twitter endpoints for 0Auth2
authorize_url = "https://twitter.com/i/oauth2/authorize"
token_url = "https://api.twitter.com/2/oauth2/token"
user_info_url = "https://api.twitter.com/2/users/me" 

@app.route("/")
def home():
    #needed for autho 2.0 with PCKE which is needed for reverse_chronological_timeline endpoint 
    code_verifier = code_verification()
    code_challenge = code_challenger(code_verifier)
    #storing code_verifier for auth code later
    session['code_verifier'] = code_verifier

    #params for auth 2.0 request
    params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scope": "tweet.read users.read",
        "state": secrets.token_urlsafe(16),
        "code_challenge": code_challenge,
        "code_challenge_method": "S256"
    }
    #creates auth url
    url = requests.Request("GET", authorize_url, params=params).prepare().url
    return redirect(url)

@app.route("/callback")
def callback():

    #gets auth code 
    code = request.args.get("code")
    state = request.args.get("state")
    #gets stored code_verifier
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

    #echanges auth code for access token
    token_response = requests.post(token_url, data=token_data, headers=headers)
    token_json = token_response.json()

    #store access token
    session['access_token'] = token_json['access_token']
    session['refresh_token'] = token_json.get('refresh_token')

    headers = {
        "Authorization": f"Bearer {session['access_token']}"
    }

    #get user info using access token
    user_info_response = requests.get(user_info_url, headers=headers)
    user_info = user_info_response.json()

    #gets users reverse chronological timeline (only twitter API V2endpoint avaiable for timeline)
    timeline_data = fetch_reverse_chronological_timeline(session['access_token'], user_info['data']['id'])

    if timeline_data:
        tweets = [tweet['text'] for tweet in timeline_data['data']]
        tweets_summarised = summarize_tweets(tweets)
        summaries = tweets_summarised.split('\n')
        summaries = [summary for summary in summaries if summary] 
        return render_template('summary.html', summaries=summaries)

    else:
        return "Failed to fetch home timeline"

def code_verification():
    code_verifier = secrets.token_urlsafe(128)
    return code_verifier

def code_challenger(code_verifier):
    code_challenge = base64.urlsafe_b64encode(hashlib.sha256(code_verifier.encode()).digest()).rstrip(b'=').decode('utf-8')
    return code_challenge

#
def fetch_reverse_chronological_timeline(access_token, user_id):
    url = f"https://api.twitter.com/2/users/{user_id}/timelines/reverse_chronological"

    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    #as this endpoint is limited to 75 per 15mins, I made the max results quite low to allow plenty of testing
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

    client = OpenAI(api_key=openai_api_key)
    tweets_text = " ".join(tweets)
    GPT_MODEL = "gpt-4o"
 
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        #gpt prompt from imaginary user 
        {"role": "user", "content": f"drill down to the context of those tweets, summarise the topics under discussion and present to the end user as summaries. I would like just the summary, No : No ** no usernames no titles or flairs or anything like that, just the summary text: {tweets}"}
    ]

    response = client.chat.completions.create(
        model=GPT_MODEL,
        messages=messages,
        temperature=0           #set temp to zero as we need to get to the drilled down context, no creative flair
    )
    #get just the gpt response from object
    tweets_summarised = response.choices[0].message.content
 
    print(tweets_summarised)
    return tweets_summarised
    
if __name__ == "__main__":
    app.run(debug=True)
