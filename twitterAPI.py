import tweepy 
import config
import pandas as pd
import json
from transformers import BartTokenizer, BartForConditionalGeneration


tokenizer = BartTokenizer.from_pretrained('facebook/bart-large-cnn')
model = BartForConditionalGeneration.from_pretrained('facebook/bart-large-cnn')

#client = tweepy.Client(bearer_token=config.BEARER_TOKEN)

query = 'dublin'

#response = client.search_recent_tweets(query=query, max_results=10)

#tweet_texts = [tweet.text for tweet in response.data]

#print(tweet_texts)

def generate_summary(text):
    inputs = tokenizer.encode("summarize: " + text, return_tensors="pt", max_length=1024, truncation=True)
    summary_ids = model.generate(inputs, max_length=150, min_length=50, length_penalty=2.0, num_beams=4, early_stopping=True)
    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    return summary

article = "I went to the shop and fell on a branch and hurt myself"
summary = generate_summary(article)
print("Original Text:", article)
print("Summary:", summary)
