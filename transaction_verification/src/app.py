import sys
import os

# This set of lines are needed to import the gRPC stubs.
# The path of the stubs is relative to the current file, or absolute inside the container.
# Change these lines only if strictly needed.
FILE = __file__ if '__file__' in globals() else os.getenv("PYTHONFILE", "")
transaction_verification_grpc_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb/transaction_verification'))
sys.path.insert(0, transaction_verification_grpc_path)
import transaction_verification_pb2 as transaction_verification
import transaction_verification_pb2_grpc as transaction_verification_grpc

import grpc
from concurrent import futures

# Create a class to define the server functions, derived from
# transaction_verification_pb2_grpc.HelloServiceServicer
class TransactionVerificationService(transaction_verification_grpc.TransactionVerificationServiceServicer):
    # Create an RPC function to say hello
    def VerifyTransaction(self, request, context):
        response = transaction_verification.TransactionVerificationResponse()
        terms_accepted = request.termsAccepted

        # Validation checks
        if any(item.quantity <= 0 for item in request.items):  # Ensure no item has 0 or negative quantity
            response.is_valid = False
            response.message = "Transaction is invalid: Item quantity cannot be zero or negative."
        elif not request.user.name or not request.user.contact:  # Check for missing user info
            response.is_valid = False
            response.message = "Transaction is invalid: Missing user information."
        elif not request.creditCard.number or not request.creditCard.expirationDate or not request.creditCard.cvv:
            response.is_valid = False
            response.message = "Transaction is invalid: Incomplete credit card details."
        elif not request.billingAddress.street or not request.billingAddress.city or not request.billingAddress.state or not request.billingAddress.zip or not request.billingAddress.country:
            response.is_valid = False
            response.message = "Transaction is invalid: Incomplete billing address."
        elif not terms_accepted:  # Validation rule: Terms must be accepted
            response.is_valid = False
            response.message = "Transaction is invalid: Terms not accepted."
        else:
            response.is_valid = True
            response.message = "Transaction is valid."

        print(f"Transaction Status: {response.message}")
        return response

def serve():
    # Create a gRPC server
    server = grpc.server(futures.ThreadPoolExecutor())
    # Add HelloService
    transaction_verification_grpc.add_TransactionVerificationServiceServicer_to_server(TransactionVerificationService(), server)
    # Listen on port 50052
    port = "50052"
    server.add_insecure_port("[::]:" + port)
    # Start the server
    server.start()
    print("Server started. Listening on port 50052.")
    # Keep thread alive
    server.wait_for_termination()

if __name__ == '__main__':
    serve()