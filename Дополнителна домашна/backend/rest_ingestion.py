import requests
import json
import time
from kafka import KafkaProducer
from config import API_SOURCES, KAFKA_BROKER, KAFKA_TOPIC

producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

last_fetched_data = {}

def fetch_data():
    """Превзема финансиски податоци од REST API и ги испраќа во Kafka."""
    global last_fetched_data

    for source, details in API_SOURCES.items():
        response = requests.get(details["url"], params=details["params"])

        if response.status_code == 200:
            data = response.json()

            if "Information" in data and "rate limit" in data["Information"]:
                print(f"[X] Лимит на API повици достигнат! Чекаме подолго пред следниот повик...")
                time.sleep(900)
                continue

            if last_fetched_data.get(source) == data:
                print(f"[~] Податоците од {source} не се сменети")
                continue

            last_fetched_data[source] = data
            producer.send(KAFKA_TOPIC, {"source": source, "data": data})
            print(f"[✓] Нови податоци испратени од {source}")

        else:
            print(f"[X] Грешка при превземање од {source}: {response.status_code}")

if __name__ == "__main__":
    while True:
        fetch_data()
        time.sleep(600)