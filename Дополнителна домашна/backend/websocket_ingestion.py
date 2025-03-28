import asyncio
import websockets
import json
from kafka import KafkaProducer
from config import KAFKA_BROKER, KAFKA_TOPIC

WEBSOCKET_URL = "wss://streamer.finance.yahoo.com"

producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

async def websocket_client():
    """Конектирање на WebSocket и праќање на податоци во Kafka"""
    while True:
        try:
            async with websockets.connect(WEBSOCKET_URL) as websocket:
                await websocket.send(json.dumps({"subscribe": ["AAPL"]}))
                print("[✓] Поврзан на WebSocket")

                while True:
                    response = await websocket.recv()
                    data = json.loads(response)

                    if "id" in data:
                        producer.send(KAFKA_TOPIC, {"source": "yahoo_ws", "data": data})
                        print(f"[✓] Примени податоци во реално време: {data}")
                    else:
                        print(f"[X] Неочекуван одговор од WebSocket: {data}")

        except Exception as e:
            print(f"[X] Проблем со WebSocket: {e}")
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(websocket_client())
