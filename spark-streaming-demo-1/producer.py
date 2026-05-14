import json
import time
import random
from datetime import datetime, timedelta
from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    key_serializer=lambda k: k.encode("utf-8"),
)

users = ["user-1", "user-2", "user-3", "user-4", "user-5"]

for i in range(60):
    key = users[i % len(users)]
    # ~20% of events are backdated 2-5 minutes to simulate late arrivals.
    if random.random() < 0.2:
        event_time = datetime.utcnow() - timedelta(minutes=random.randint(1, 3))
    else:
        event_time = datetime.utcnow()

    message = {
        "id": i,
        "user": key,
        "action": "click",
        "event_time": event_time.isoformat(),
    }
    producer.send("events", key=key, value=message)
    print(f"sent: key={key} event_time={message['event_time']}")
    time.sleep(0.5)

producer.flush()
producer.close()