import sys
import os

# This set of lines are needed to import the gRPC stubs.
# The path of the stubs is relative to the current file, or absolute inside the container.
# Change these lines only if strictly needed.
FILE = __file__ if '__file__' in globals() else os.getenv("PYTHONFILE", "")
fraud_detection_grpc_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb/fraud_detection'))
sys.path.insert(0, fraud_detection_grpc_path)
import fraud_detection_pb2 as fraud_detection
import fraud_detection_pb2_grpc as fraud_detection_grpc

import grpc
from concurrent import futures

#imported from the utils fraud_detection
class FraudDetectionService(fraud_detection_grpc.FraudDetectionServiceServicer):
    def FraudDetection(self, request, context):
        total_qty = sum(item.quantity for item in request.items)  # Calculate total quantity

        response = fraud_detection.FraudResponse()
        
        # Example fraud detection rule: flag if total quantity exceeds 100
        if total_qty > 100:
            response.is_valid = False
            response.message = "Transaction is fraud: Too many items ordered."
        elif request.creditCard.number.startswith("0000"):  # Example fraud rule for invalid card numbers
            response.is_valid = False
            response.message = "Transaction is fraud: Invalid credit card number."
        else:
            response.is_valid = True
            response.message = "Transaction is not fraud."
        
        print(response.message)
        return response

def serve():
    # Create a gRPC server
    server = grpc.server(futures.ThreadPoolExecutor())
    # Add HelloService
    fraud_detection_grpc.add_FraudDetectionServiceServicer_to_server(FraudDetectionService(), server)
    # Listen on port 50051
    port = "50051"
    server.add_insecure_port("[::]:" + port)
    # Start the server
    server.start()
    print("Server started. Listening on port 50051.")
    # Keep thread alive
    server.wait_for_termination()

if __name__ == '__main__':
    serve()