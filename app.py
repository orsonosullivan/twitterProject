from flask import Flask


#load enviromental variables 
load_dotenv()

app = Flask(__name__)

@app.route('/')
def home():
    return 'Welcome to my Reassessment!'

if __name__ == '__main__':
    app.run()