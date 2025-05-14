from concurrent import futures

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import grpc
from proto import post_service_pb2
from proto import post_service_pb2_grpc
from post_grpc import PostServiceImpl
import json

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    post_service_pb2_grpc.add_PostServiceServicer_to_server(PostServiceImpl(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("gRPC server started on port 50051")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()