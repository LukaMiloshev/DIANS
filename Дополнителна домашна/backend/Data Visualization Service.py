from fastapi import FastAPI
import psycopg2
import pandas as pd
import plotly.express as px
import plotly.io as pio
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

PG_HOST = "localhost"
PG_DB = "financial_data"
PG_USER = "postgres"
PG_PASSWORD = "your_password"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def fetch_data():
    conn = psycopg2.connect(host=PG_HOST, database=PG_DB, user=PG_USER, password=PG_PASSWORD)
    query = "SELECT timestamp, close FROM aggregated_data ORDER BY timestamp ASC"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

@app.get("/chart")
def get_chart():
    df = fetch_data()
    fig = px.line(df, x='timestamp', y='close', title='Stock Price Trends')
    graph_json = pio.to_json(fig)
    return JSONResponse(content=graph_json)