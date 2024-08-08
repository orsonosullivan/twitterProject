from flask import Flask, redirect, url_for, render_template, request
from authlib.integration.flask_client import OAuth
from dotenv import load_dotenv
import tweepy 
import config

load_dot_env()

app = Flask(__name__)

#client = tweepy.Client(bearer_token=config.BEARER_TOKEN)

#query = 'dublin'

#response = client.search_recent_tweets(query=query, max_results=10)

#tweet_texts = [tweet.text for tweet in response.data]

#print(tweet_texts)

#search function using tweepy 
def process_query(query):
    client = tweepy.Client(bearer_token=config.BEARER_TOKEN)
    response = client.search_recent_tweets(query=query, max_results=10)
    tweet_texts = [tweet.text for tweet in response.data]
    tweet_texts = str_replace_all(tweets_list, "[\r\n]" , "")

    print (tweet_texts)
    return f"Processed tweets: {tweet_texts}"

#landing page 
@app.route("/")
def home():
    return render_template("welcomepage.html")

#search function
@app.route('/search', methods=['POST'])
def search():
    query = request.form['query']
    result = process_query(query)
    return render_template('resultpage.html', query=query,result=result)

if __name__ == "__main__":
    app.run()
