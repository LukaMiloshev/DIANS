import numpy as np
import pandas as pd
import psycopg2
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
import matplotlib.pyplot as plt
from cassandra.cluster import Cluster
from sklearn.preprocessing import MinMaxScaler

PG_HOST = "localhost"
PG_DB = "financial_data"
PG_USER = "postgres"
PG_PASSWORD = "your_password"

CASSANDRA_HOSTS = ["127.0.0.1"]
CASSANDRA_KEYSPACE = "financial"

def fetch_postgres_data():
    conn = psycopg2.connect(host=PG_HOST, database=PG_DB, user=PG_USER, password=PG_PASSWORD)
    query = "SELECT timestamp, close FROM aggregated_data ORDER BY timestamp ASC"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def fetch_cassandra_data():
    cluster = Cluster(CASSANDRA_HOSTS)
    session = cluster.connect()
    session.set_keyspace(CASSANDRA_KEYSPACE)
    query = "SELECT timestamp, close FROM aggregated_data"
    rows = session.execute(query)
    df = pd.DataFrame(rows, columns=['timestamp', 'close'])
    cluster.shutdown()
    return df

postgres_data = fetch_postgres_data()
cassandra_data = fetch_cassandra_data()
data = pd.concat([postgres_data, cassandra_data]).drop_duplicates().sort_values(by='timestamp')

scaler = MinMaxScaler(feature_range=(0,1))
data_scaled = scaler.fit_transform(data[['close']])

sequence_length = 50
X, y = [], []
for i in range(len(data_scaled) - sequence_length):
    X.append(data_scaled[i:i+sequence_length])
    y.append(data_scaled[i+sequence_length])
X, y = np.array(X), np.array(y)

model = Sequential([
    LSTM(units=50, return_sequences=True, input_shape=(X.shape[1], 1)),
    Dropout(0.2),
    LSTM(units=50, return_sequences=False),
    Dropout(0.2),
    Dense(units=25),
    Dense(units=1)
])

model.compile(optimizer='adam', loss='mean_squared_error')

model.fit(X, y, epochs=10, batch_size=32)

predicted_prices = model.predict(X)
predicted_prices = scaler.inverse_transform(predicted_prices)

plt.plot(data['timestamp'][sequence_length:], predicted_prices, label='Predicted Price')
plt.plot(data['timestamp'], data['close'], label='Actual Price')
plt.legend()
plt.show()