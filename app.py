from flask import Flask, render_template
from newsapi import NewsApiClient

app = Flask(__name__)

# Initialize News API client
newsapi = NewsApiClient(api_key='b977db904b954b54b03e468179309596')

@app.route('/')
def dashboard():
    # Fetch top headlines
    top_headlines = newsapi.get_top_headlines(category='business', language='en', country='us')
    
    # Get the articles from the response
    articles = top_headlines['articles']
    
    # Pass articles to the template to render
    return render_template('dashboard.html', articles=articles)

if __name__ == '__main__':
    app.run(debug=True)


