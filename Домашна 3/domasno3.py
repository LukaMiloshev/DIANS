import numpy as np
import pandas as pd
from flask import Flask, jsonify, request
import requests
from bs4 import BeautifulSoup
from ta.momentum import RSIIndicator
from ta.trend import SMAIndicator, EMAIndicator, MACD
from ta.volatility import BollingerBands
from ta.volume import OnBalanceVolumeIndicator
import matplotlib.pyplot as plt
from datetime import datetime
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

app = Flask(__name__)

# Step 1: Fetch Data from Seinet
def fetch_data_from_seinet(symbol):
    base_url = "https://seinet.com.mk/stock-data/"
    response = requests.get(f"{base_url}{symbol}")
    soup = BeautifulSoup(response.content, "html.parser")

    table = soup.find("table", {"id": "historical-data"})
    if not table:
        return None

    rows = table.find_all("tr")
    data = []
    for row in rows[1:]:
        cols = row.find_all("td")
        if len(cols) >= 6:
            data.append({
                "Date": cols[0].text.strip(),
                "Open": float(cols[1].text.strip().replace(",", "")),
                "High": float(cols[2].text.strip().replace(",", "")),
                "Low": float(cols[3].text.strip().replace(",", "")),
                "Close": float(cols[4].text.strip().replace(",", "")),
                "Volume": int(cols[5].text.strip().replace(",", ""))
            })

    df = pd.DataFrame(data)
    df['Date'] = pd.to_datetime(df['Date'], format='%d.%m.%Y')
    df.set_index('Date', inplace=True)
    df.sort_index(inplace=True)
    return df

# Step 2: Calculate Technical Indicators
def calculate_indicators(df):
    df['SMA_50'] = SMAIndicator(df['Close'], window=50).sma_indicator()
    df['SMA_200'] = SMAIndicator(df['Close'], window=200).sma_indicator()
    df['EMA_20'] = EMAIndicator(df['Close'], window=20).ema_indicator()
    df['RSI'] = RSIIndicator(df['Close'], window=14).rsi()
    df['MACD'] = MACD(df['Close']).macd()
    df['MACD_Signal'] = MACD(df['Close']).macd_signal()
    bollinger = BollingerBands(df['Close'])
    df['BB_High'] = bollinger.bollinger_hband()
    df['BB_Low'] = bollinger.bollinger_lband()
    df['OBV'] = OnBalanceVolumeIndicator(df['Close'], df['Volume']).on_balance_volume()
    return df

# Step 3: Generate Buy/Sell/Hold Signals
def generate_signals(df):
    df['Signal'] = 'Hold'
    df.loc[df['RSI'] < 30, 'Signal'] = 'Buy'
    df.loc[df['RSI'] > 70, 'Signal'] = 'Sell'
    df.loc[(df['Close'] > df['SMA_50']) & (df['Close'] > df['SMA_200']), 'Signal'] = 'Buy'
    df.loc[(df['Close'] < df['SMA_50']) & (df['Close'] < df['SMA_200']), 'Signal'] = 'Sell'
    return df

# Step 4: Aggregate Data into Different Timeframes
def aggregate_timeframes(df):
    daily = df.copy()
    weekly = df.resample('W').agg({
        'Open': 'first',
        'High': 'max',
        'Low': 'min',
        'Close': 'last',
        'Volume': 'sum',
        'SMA_50': 'last',
        'SMA_200': 'last',
        'EMA_20': 'last',
        'RSI': 'last',
        'MACD': 'last',
        'MACD_Signal': 'last',
        'BB_High': 'last',
        'BB_Low': 'last',
        'OBV': 'last',
        'Signal': 'last'
    })
    monthly = df.resample('M').agg({
        'Open': 'first',
        'High': 'max',
        'Low': 'min',
        'Close': 'last',
        'Volume': 'sum',
        'SMA_50': 'last',
        'SMA_200': 'last',
        'EMA_20': 'last',
        'RSI': 'last',
        'MACD': 'last',
        'MACD_Signal': 'last',
        'BB_High': 'last',
        'BB_Low': 'last',
        'OBV': 'last',
        'Signal': 'last'
    })
    return daily, weekly, monthly

# Step 5: Sentiment Analysis
def sentiment_analysis_score(text):
    sentiment_tool = SentimentIntensityAnalyzer()
    scores = sentiment_tool.polarity_scores(text)
    return scores['compound']

# Step 6: Fetch News and Analyze Sentiment
def get_news_and_sentiment(symbol):
    base_url = f"https://www.mse.mk/mk/search/{symbol}"
    resp = requests.get(base_url)
    if resp.status_code == 200:
        soup = BeautifulSoup(resp.text, 'html.parser')
        link = soup.find('div', class_='news-list').find('a', href=True)
        if link:
            news_url = f"https://www.mse.mk{link['href']}"
            news_response = requests.get(news_url)
            if news_response.status_code == 200:
                sentiment_value = sentiment_analysis_score(news_response.text)
                return sentiment_value, news_url
    return None, None

# Step 7: Flask Endpoint for Analysis
@app.route('/analyze', methods=['POST'])
def analyze_endpoint():
    symbol = request.json.get('symbol')
    df = fetch_data_from_seinet(symbol)
    if df is None:
        return jsonify({'error': 'Stock data not found.'}), 404

    df = calculate_indicators(df)
    df = generate_signals(df)
    sentiment_value, news_url = get_news_and_sentiment(symbol)

    daily, weekly, monthly = aggregate_timeframes(df)
    latest_signal = daily.iloc[-1]['Signal']

    return jsonify({
        'symbol': symbol,
        'latest_signal': latest_signal,
        'sentiment_value': sentiment_value,
        'news_url': news_url,
        'data_preview': daily.tail(5).to_dict()
    })

if __name__ == '__main__':
    app.run(debug=True)
