import json
import os
from datetime import datetime
from typing import Dict, Any, Optional
from confluent_kafka import Producer

# Kafka configuration
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")


class KafkaProducer:
    def __init__(self):
        self.producer = Producer({
            'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
            'client.id': 'post_service_producer'
        })
        
        # Define topics
        self.USER_REGISTERED_TOPIC = "user_registered"
        self.POST_VIEWED_TOPIC = "post_viewed"
        self.POST_LIKED_TOPIC = "post_liked"
        self.POST_COMMENTED_TOPIC = "post_commented"
    
    def _delivery_report(self, err, msg):
        """Called once for each message produced to indicate delivery result."""
        if err is not None:
            print(f'Message delivery failed: {err}')
        else:
            print(f'Message delivered to {msg.topic()} [{msg.partition()}]')
    
    def _serialize_datetime(self, obj):
        """JSON serializer for datetime objects."""
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Type {type(obj)} not serializable")
    
    def send_event(self, topic: str, data: Dict[str, Any], key: Optional[str] = None):
        """Send an event to the specified Kafka topic."""
        payload = json.dumps(data, default=self._serialize_datetime).encode('utf-8')
        self.producer.produce(
            topic=topic,
            key=key.encode('utf-8') if key else None,
            value=payload,
            callback=self._delivery_report
        )
        # Flush to ensure message is sent immediately
        self.producer.flush()
    
    def send_comment_created_event(self, comment_data: Dict[str, Any]):
        """Send event when a book is created."""
        self.send_event(
            topic=self.POST_COMMENTED_TOPI,
            data={
                "event_type": "post_commented",
                "timestamp": datetime.now(),
                "comment": comment_data
            },
            key=str(comment_data["id"])
        )
    
    def send_post_viewed_event(self, post_id: str, user_id: str):
        """Send event when a book is viewed."""
        self.send_event(
            topic=self.POST_VIEWED_TOPIC,
            data={
                "event_type": "post_viewed",
                "timestamp": datetime.now(),
                "post_id": post_id,
                "user_id": user_id
            },
            key=str(post_id)
        )
    
    def send_post_liked_event(self, post_id: str, user_id: str):
        """Send event when a book is liked."""
        self.send_event(
            topic=self.POST_LIKED_TOPIC,
            data={
                "event_type": "post_liked",
                "timestamp": datetime.now(),
                "post_id": post_id,
                "user_id": user_id
            },
            key=str(user_id)
        ) 