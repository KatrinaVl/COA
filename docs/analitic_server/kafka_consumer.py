import os
import json
from confluent_kafka import Consumer, KafkaException, KafkaError
from clickhouse_client import post_liked, post_seen, post_commented
from datetime import datetime

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
GROUP_ID = os.getenv("KAFKA_CONSUMER_GROUP", "analytics_test_group")

class KafkaAnalyticsConsumer:
    def __init__(self, topics):
        self.consumer = Consumer({
            'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
            'group.id': GROUP_ID,
            'auto.offset.reset': 'earliest'
        })
        self.consumer.subscribe(topics)
        print(f"Subscribed to topics: {topics}", flush=True)

    def consume_messages(self):
        try:
            print(f"Listening to Kafka topics...", flush=True)
            while True:
                msg = self.consumer.poll(1.0)
                if msg is None:
                    continue
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        continue
                    else:
                        raise KafkaException(msg.error())
                else:
                    print(f"Get message", flush=True)
                    self.process_message(msg)
        finally:
            self.consumer.close()

    def process_message(self, msg):
        try:
            data = json.loads(msg.value().decode('utf-8'))
            topic = msg.topic()
            print(f"[{topic}] Received event: {data}")

            if topic == "post_viewed":
                self.handle_post_viewed(data)
            elif topic == "post_liked":
                self.handle_post_liked(data)
            elif topic == "post_commented":
                self.handle_post_commented(data)
            else:
                print(f"Unknown topic: {topic}")

        except json.JSONDecodeError as e:
            print(f"Failed to decode message: {e}")


    def handle_post_viewed(self, data):
        print("Post viewed:", flush = True)
        post_seen(data)

    def handle_post_liked(self, data):
        print(f"Post liked:", flush = True)

        post_liked(data)

    def handle_post_commented(self, data):
        print("Post commented:", flush = True)
        post_commented(data)
