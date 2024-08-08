from flask import Flask, redirect, url_for, render_template, request
from authlib.integration.flask_client import OAuth
from dotenv import load_dotenv
import tweepy 
import config

load_dot_env()

app = Flask(__name__)

app.config["TWITTER_CLIENT_ID"] = os.getenv("TWITTER_CLIENT_ID")
app.config["TWITTER_CLIENT_SECRET"] = os.getenv("TWITTER_CLIENT_SECRET")
app.config["TWITTER_DOMAIN"] = os.getenv("TWITTER_DOMAIN")
app.config["TWITTER_CALLBACK_URL"] = os.getenv("TWITTER_CALLBACK_URL")

oauth = OAuth(app)

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
