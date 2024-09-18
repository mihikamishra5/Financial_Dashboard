from flask import Flask, render_template_string
import dash
from dash import dcc, html
import plotly.express as px
import pandas as pd
from newsapi import NewsApiClient

# Initialize Flask app
app = Flask(__name__)

# Initialize Dash app and bind it to the Flask app
dash_app = dash.Dash(__name__, server=app, url_base_pathname='/dashboard/', serve_locally=True)

# Initialize NewsAPI client (replace with your NewsAPI key)
newsapi = NewsApiClient(api_key='b977db904b954b54b03e468179309596')

# Example DataFrames (replace with real-time data)
stock_data = pd.DataFrame({
    'Stock': ['AAPL', 'GOOGL', 'AMZN'],
    'Price': [145.09, 2738.27, 3527.83],
    'Sector': ['tech', 'tech', 'tech']
})

crypto_data = pd.DataFrame({
    'Crypto': ['Bitcoin', 'Ethereum', 'Ripple'],
    'Price': [45000, 3200, 1.15]
})

commodity_data = pd.DataFrame({
    'Commodity': ['Gold', 'Silver', 'Oil'],
    'Price': [1800, 23.45, 70]
})

# Global Markets Data
global_markets_data = pd.DataFrame({
    'Region': ['US', 'Europe', 'Asia'],
    'Market Index': [4500, 3450, 1200]
})

# Fetch financial news using NewsAPI
def fetch_financial_news():
    news_data = newsapi.get_top_headlines(category='business', language='en', country='us')
    articles = news_data['articles']
    return pd.DataFrame(articles)

news_df = fetch_financial_news()

# Dash layout with multiple panels
dash_app.layout = html.Div([
    html.H1('Real-Time Financial News Dashboard', style={'textAlign': 'center'}),

    # Stock panel
    html.Div([
        html.H2('Stocks'),
        dcc.Graph(figure=px.bar(stock_data, x='Stock', y='Price', title='Stock Prices'), id='stock-graph')
    ], className='six columns'),

    # Crypto panel
    html.Div([
        html.H2('Cryptocurrencies'),
        dcc.Graph(figure=px.pie(crypto_data, names='Crypto', values='Price', title='Crypto Prices'))
    ], className='six columns'),

    # Commodities panel
    html.Div([
        html.H2('Commodities'),
        dcc.Graph(figure=px.bar(commodity_data, x='Commodity', y='Price', title='Commodity Prices'))
    ], className='six columns'),

    # Global Markets panel
    html.Div([
        html.H2('Global Markets'),
        dcc.Graph(figure=px.bar(global_markets_data, x='Region', y='Market Index', title='Global Market Indices'))
    ], className='six columns'),

    # Financial news display
    html.Div([
        html.H2('Latest Financial News'),
        html.Ul([html.Li(html.A(article['title'], href=article['url'], target='_blank')) for _, article in news_df.iterrows()])
    ], className='six columns')
], className='row')

# Flask route for the combined page
@app.route('/')
def dashboard():
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Real-Time Financial Dashboard</title>
        <link rel="stylesheet" href="{{ url_for('static', filename='css/styles.css') }}">
    </head>
    <body>
        <div class="container">
            <h1>Real-Time Financial Dashboard</h1>
            <div>
                {%include 'dashboard.html'%}
            </div>
        </div>
    </body>
    </html>
    ''')

# Dropdown for filtering stock sectors
dash_app.layout.children.insert(0, html.Div([
    html.Label('Select Stock Sector'),
    dcc.Dropdown(
        id='sector-filter',
        options=[
            {'label': 'Technology', 'value': 'tech'},
            {'label': 'Healthcare', 'value': 'health'},
            {'label': 'Energy', 'value': 'energy'}
        ],
        value='tech'
    )
], className='six columns'))

# Callback to update stock data based on selected sector
@dash_app.callback(
    dash.dependencies.Output('stock-graph', 'figure'),
    [dash.dependencies.Input('sector-filter', 'value')]
)
def update_stock_chart(selected_sector):
    filtered_data = stock_data[stock_data['Sector'] == selected_sector]
    return px.bar(filtered_data, x='Stock', y='Price', title=f'{selected_sector.capitalize()} Stock Prices')

if __name__ == '__main__':
    app.run(debug=True)
