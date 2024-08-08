from flask import Flask, redirect, url_for, render_template
import tweepy 
import config

app = Flask(__name__)

client = tweepy.Client(bearer_token=config.BEARER_TOKEN)

query = 'dublin'

response = client.search_recent_tweets(query=query, max_results=10)

tweet_texts = [tweet.text for tweet in response.data]

print(tweet_texts)



@app.route("/")
def home():
    return render_template("welcomepage.html")


@approute('/search', methods=['POST'])
def search():
    searchTerm = request.form['query']
    result = process_query(query)
    return render_template('result.html', query=query,result=result)


if __name__ == "__main__":
    app.run()
