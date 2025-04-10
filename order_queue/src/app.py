import threading
import sys
import os
from collections import deque



FILE = __file__ if '__file__' in globals() else os.getenv("PYTHONFILE", "")
utils_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb/order_queue'))
sys.path.insert(0, utils_path)
import order_queue_pb2 as order_queue
import order_queue_pb2_grpc as order_queue_grpc


import grpc
from concurrent import futures



class OrderQueueService(order_queue_grpc.OrderQueueServiceServicer):
    def __init__(self):
        self._lock = threading.Lock()
        self._queue = deque() # Could be replaced with a priority structure

    def Enqueue(self, request, context):
        with self._lock:  # Ensure thread safety
            print("Order queue service called")
            self._queue.append(request.order)  # Add orderId to the queue
            print(f"Order enqueued: {request.order}")
            return order_queue.EnqueueResponse(success=True, message="Order enqueued successfully")

    def Dequeue(self, request, context):
        print(f"Order queue service called by executor {request.executor_id}")
        with self._lock:  # Ensure thread safety
            if self._queue:  # Check if the queue is not empty
                order = self._queue.popleft()  # Remove and get the first order
                print(f"Order dequeued: {order}")
                return order_queue.DequeueResponse(success=True, order=order)
            else:
                empty_order = order_queue.Order(orderId=0, userName="")
                return order_queue.DequeueResponse(success=False, order=empty_order)

def serve_queue_service():
    # TODO: create gRPC server, add OrderQueueService, start server
    # Create a gRPC server
    server = grpc.server(futures.ThreadPoolExecutor())
    # Add HelloService
    order_queue_grpc.add_OrderQueueServiceServicer_to_server(OrderQueueService(), server)
    # Listen on port 50054
    port = "50054"
    server.add_insecure_port("[::]:" + port)
    # Start the server
    server.start()
    print("Server started. Listening on port 50054.")    
    #time.sleep(5)
    #call_all_executors()
    # Keep thread alive
    server.wait_for_termination()

if __name__ == '__main__':
    serve_queue_service()