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

# 3 rooms, each with a distinct baseline temperature so output is easy to scan.
rooms = {
    "kitchen": 72.0,
    "garage":  55.0,
    "attic":   88.0,
}

for i in range(60):
    room = list(rooms.keys())[i % len(rooms)]
    baseline = rooms[room]
    temp = round(baseline + random.uniform(-1.5, 1.5), 1)

    # The attic sensor has flaky wifi: ~50% of its readings arrive 1-3 min late.
    # Other rooms are always on time.
    is_late = (room == "attic" and random.random() < 0.5)
    if is_late:
        event_time = datetime.utcnow() - timedelta(minutes=random.randint(1, 5))
    else:
        event_time = datetime.utcnow()

    message = {
        "id": i,
        "room": room,
        "temp": temp,
        "event_time": event_time.isoformat(),
    }
    producer.send("sensors", key=room, value=message)

    tag = "  [LATE]" if is_late else ""
    print(f"sent: room={room:<8} temp={temp:<5} event_time={message['event_time']}{tag}")
    time.sleep(0.5)

producer.flush()
producer.close()