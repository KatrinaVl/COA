import threading
import grpc
from concurrent import futures
import time

from kafka_consumer import KafkaAnalyticsConsumer
from proto import analitic_service_pb2_grpc
from analitic_grpc import AnaliticServiceImpl
from clickhouse_client import init_clickhouse

KAFKA_TOPICS = ["user_registered", "post_viewed", "post_liked", "post_commented"]

def start_kafka_consumer():
    print("Start kafka consumer", flush=True)
    consumer = KafkaAnalyticsConsumer(KAFKA_TOPICS)
    consumer.consume_messages()

def serve_grpc():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    analitic_service_pb2_grpc.add_AnaliticServiceServicer_to_server(AnaliticServiceImpl(), server)
    server.add_insecure_port('[::]:50052')
    server.start()
    print("gRPC server started on port 50052")
    server.wait_for_termination()

if __name__ == "__main__":
    print("Running analitic_server.py", flush=True)

    print("Initializing ClickHouse...", flush=True)
    init_clickhouse()
    print("ClickHouse initialized", flush=True)
    kafka_thread = threading.Thread(target=start_kafka_consumer, daemon=True)
    kafka_thread.start()
    print("Kafka consumer thread started", flush=True)

    serve_grpc()