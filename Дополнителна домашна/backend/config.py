KAFKA_BROKER = "localhost:9092"
KAFKA_TOPIC = "financial_data"

API_SOURCES = {
    "alpha_vantage": {
        "url": "https://www.alphavantage.co/query",
        "api_key": "ID2A83X46V6FFQ1R",
        "params": {
            "function": "TIME_SERIES_INTRADAY",
            "symbol": "AAPL",
            "interval": "1min"
        }
    }
}
