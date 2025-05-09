import grpc
from concurrent import futures
import time
import sys 
import os

FILE = __file__ if '__file__' in globals() else os.getenv("PYTHONFILE", "")
utils_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb/payment_service')) # Adjust path components as needed
sys.path.insert(0, utils_path)
import payment_service_pb2 as payment
import payment_service_pb2_grpc as payment_grpc

class PaymentService(payment_grpc.PaymentServiceServicer):
    def __init__(self):
        self._prepared_orders = set() # To track orders that have been prepared

    def Prepare(self, request, context):
        print(f"PaymentService: Received Prepare for order {request.order_id}")
        # Dummy validation logic: always ready for this example
        # In a real system, this would involve checking funds, etc.
        self._prepared_orders.add(request.order_id)
        return payment.PrepareResponse(ready=True)

    def Commit(self, request, context):
        print(f"PaymentService: Received Commit for order {request.order_id}")
        if request.order_id in self._prepared_orders:
            # Simulate payment processing
            print(f"Payment committed for order {request.order_id}")
            self._prepared_orders.discard(request.order_id)
            return payment.CommitResponse(success=True)
        else:
            # Should not happen in a correct 2PC flow if Prepare was successful
            print(f"PaymentService: Commit received for unprepared order {request.order_id}")
            return payment.CommitResponse(success=False)


    def Abort(self, request, context):
        print(f"PaymentService: Received Abort for order {request.order_id}")
        if request.order_id in self._prepared_orders:
             print(f"Payment aborted for order {request.order_id}")
             self._prepared_orders.discard(request.order_id)
        return payment.AbortResponse(aborted=True)

def serve_payment_service(port):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    payment_grpc.add_PaymentServiceServicer_to_server(PaymentService(), server)
    server.add_insecure_port(f'[::]:{port}')
    server.start()
    print(f"Payment Service started. Listening on port {port}.")
    server.wait_for_termination()

if __name__ == '__main__':
    # Example usage: serve on port 50061
    serve_payment_service("50061")