from kafka import KafkaConsumer
import json

KAFKA_TOPIC = 'scene'
KAFKA_SERVER = 'localhost:9092'

consumer = KafkaConsumer(
    KAFKA_TOPIC,
    bootstrap_servers=KAFKA_SERVER,
    auto_offset_reset='earliest',
    value_deserializer=lambda v: json.loads(v.decode('utf-8')),
    group_id='new_group_id' 
)

print('Listening to', KAFKA_TOPIC)

for message in consumer:
    data = {
        'start_date': message.value['start_date'],
        'end_date': message.value['end_date'],
        'strategy': message.value['strategy']
    }

    print(data)

    with open('sample.json', 'w') as f:
        json.dump(data, f)
