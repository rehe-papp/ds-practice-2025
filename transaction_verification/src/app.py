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
    def __init__(self):
        self.order_data = {}  # Store order data and vector clocks
    
    def InitializeVerification(self, request, context):
        order_id = request.order_id
        self.order_data[order_id] = {
            "request": request,
            "vector_clock": dict(request.vector_clock.clock) # store vector clock as dict
        }
        print(f"Transaction Verification: Initialized order {order_id} with vector clock {self.order_data[order_id]['vector_clock']}")
        return transaction_verification.TransactionVerificationResponse(is_valid=True) #return a success response

    def ProcessVerification(self, request, context):
        order_id = request.order_id
        if order_id not in self.order_data:
            return transaction_verification.TransactionVerificationResponse(is_valid=False, message="Order not initialized.")

        order_info = self.order_data[order_id]
        terms_accepted = request.termsAccepted

        # Update vector clock
        self.update_vector_clock(order_id, dict(request.vector_clock.clock)) #update with passed in vector clock
        print(f"Transaction Verification: Processing order {order_id} with vector clock {self.order_data[order_id]['vector_clock']}")

        response = transaction_verification.TransactionVerificationResponse()

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

        response.vector_clock.clock.update(self.order_data[order_id]["vector_clock"]) # send back updated vector clock
        print(f"Transaction Verification: Processed order {order_id}. Result: {response.message}")
        return response
    
    
    def ClearData(self, request, context):
        print(f"ClearData - Before update: {request.vector_clock.clock}")
        order_id = request.order_id
        final_vc = dict(request.vector_clock.clock)
        print(f"ClearData - final_vc: {final_vc}")
        if order_id in self.order_data:
            local_vc = self.order_data[order_id]["vector_clock"]
            print(f"ClearData - local_vc: {local_vc}")
            if self.is_vector_clock_less_than_or_equal(local_vc, final_vc):
                del self.order_data[order_id]
                print(f"Transaction Verification: Cleared data for order {order_id}")
                return transaction_verification.ClearDataResponse(success=True)
            else:
                print(f"Transaction Verification: Vector clock mismatch for order {order_id}. Data not cleared.")
                return transaction_verification.ClearDataResponse(success=False)
        else:
            return transaction_verification.ClearDataResponse(success=True) #if order id is not in the stored data, it is already cleared

    def update_vector_clock(self, order_id, received_vc):
        local_vc = self.order_data[order_id]["vector_clock"]
        for key, value in received_vc.items():
            local_vc[key] = max(local_vc.get(key, 0), value)
        local_vc["transaction_verification"] = local_vc.get("transaction_verification", 0) + 1

    def is_vector_clock_less_than_or_equal(self, local_vc, final_vc):
        #print(f"is_vector_clock_less_than_or_equal - local_vc: {local_vc}, final_vc: {final_vc}")
        for key, value in local_vc.items():
            if key not in final_vc or value > final_vc.get(key, 0): #changed final_vc[key] to final_vc.get(key,0)
                #print(f"is_vector_clock_less_than_or_equal - False: key={key}, local_value={value}, final_value={final_vc.get(key)}")
                return False
        #print("is_vector_clock_less_than_or_equal - True")
        return True

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