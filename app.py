from flask import Flask, render_template_string
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import requests
import os

# Initialize Flask app
app = Flask(__name__)

# Initialize Dash app and bind it to the Flask app
dash_app = dash.Dash(__name__, server=app, url_base_pathname='/dashboard/', serve_locally=True)

# API Key for Alpha Vantage
ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')

# Fetch stock data from Alpha Vantage
def fetch_stock_data(symbol='AAPL'):
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=60min&apikey={ALPHA_VANTAGE_API_KEY}'
    response = requests.get(url).json()
    time_series = response.get('Time Series (60min)', {})
    df = pd.DataFrame.from_dict(time_series, orient='index').astype(float)
    df['date'] = pd.to_datetime(df.index)
    df.rename(columns={"4. close": "Close Price"}, inplace=True)
    return df

# Fetch cryptocurrency data using CoinGecko API
def fetch_crypto_data():
    COINGECKO_API_URL = 'https://api.coingecko.com/api/v3/simple/price'
    params = {'ids': 'bitcoin,ethereum,ripple', 'vs_currencies': 'usd'}
    response = requests.get(COINGECKO_API_URL, params=params).json()
    return pd.DataFrame(response).T

# Dash layout
dash_app.layout = html.Div([
    html.H1('Real-Time Financial Dashboard', style={'textAlign': 'center', 'color': '#00aaff'}),
    
    # Stock symbol selection dropdown
    html.Div([
        html.Label('Select Stock Symbol', style={'color': '#ffffff'}),
        dcc.Dropdown(
            id='stock-symbol',
            options=[
                {'label': 'Apple', 'value': 'AAPL'},
                {'label': 'Google', 'value': 'GOOGL'},
                {'label': 'Amazon', 'value': 'AMZN'},
                {'label': 'Microsoft', 'value': 'MSFT'}
            ],
            value='AAPL'
        ),
    ], style={'width': '48%', 'margin': 'auto'}),
    
    # Stock Panel
    html.Div(id='stock-output', className='panel', style={'color': '#ffffff'}),

    # Crypto Panel
    html.Div([
        html.H2('Cryptocurrency Prices (USD)', style={'textAlign': 'center'}),
        dcc.Graph(id='crypto-prices'),
    ], className='panel', style={'color': '#ffffff'}),

    # Real-time update interval (every minute)
    dcc.Interval(
        id='interval-component',
        interval=60*1000,  # Update every minute
        n_intervals=0
    )
], style={'backgroundColor': '#1f2d3d', 'padding': '20px'})

# Callback for stock panel
@dash_app.callback(
    Output('stock-output', 'children'),
    [Input('stock-symbol', 'value'), Input('interval-component', 'n_intervals')]
)
def update_stock_panel(selected_symbol, n):
    stock_data = fetch_stock_data(selected_symbol)
    fig = px.line(stock_data, x=stock_data['date'], y="Close Price", title=f'{selected_symbol} Stock Price (Real-Time)')
    return dcc.Graph(figure=fig)

# Callback for crypto panel
@dash_app.callback(
    Output('crypto-prices', 'figure'),
    [Input('interval-component', 'n_intervals')]
)
def update_crypto_prices(n):
    crypto_data = fetch_crypto_data()
    fig = px.bar(crypto_data, x=crypto_data.index, y='usd', title='Crypto Prices (Bitcoin, Ethereum, Ripple)', labels={'x': 'Crypto', 'y': 'Price (USD)'})
    return fig

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

if __name__ == '__main__':
    app.run(debug=True)

