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
    def __init__(self):
        self.order_data = {}  # Store order data and vector clocks

    def InitializeFraud(self, request, context):
        order_id = request.order_id
        self.order_data[order_id] = {
            "request": request,
            "vector_clock": dict(request.vector_clock.clock) # store vector clock as dict
        }
        print(f"Fraud Detection: Initialized order {order_id} with vector clock {self.order_data[order_id]['vector_clock']}")
        return fraud_detection.FraudResponse(is_valid=True) #return a success response
    
    def ProcessFraud(self, request, context):
        order_id = request.order_id
        if order_id not in self.order_data:
            return fraud_detection.FraudResponse(is_valid=False, message="Order not initialized.")

        order_info = self.order_data[order_id]
        stored_request = order_info["request"]

        # Update vector clock with received clock
        self.update_vector_clock(order_id, dict(request.vector_clock.clock))
        print(f"Fraud Detection: Processing order {order_id} with vector clock {self.order_data[order_id]['vector_clock']}")

        total_qty = sum(item.quantity for item in stored_request.items)

        response = fraud_detection.FraudResponse()

        if total_qty > 100:
            response.is_valid = False
            response.message = "Transaction is fraud: Too many items ordered."
        elif stored_request.creditCard.number.startswith("0000"):
            response.is_valid = False
            response.message = "Transaction is fraud: Invalid credit card number."
        else:
            response.is_valid = True
            response.message = "Transaction is not fraud."

        # Increment fraud_detection's own clock before returning
        self.order_data[order_id]["vector_clock"]["fraud_detection"] = self.order_data[order_id]["vector_clock"].get("fraud_detection", 0) + 1

        # Send back updated vector clock
        response.vector_clock.clock.update(self.order_data[order_id]["vector_clock"])
        print(f"Fraud Detection: Processed order {order_id}. Result: {response.message}")
        return response

    def ClearData(self, request, context):
        order_id = request.order_id
        final_vc = dict(request.vector_clock.clock)

        if order_id in self.order_data:
            local_vc = self.order_data[order_id]["vector_clock"]
            if self.is_vector_clock_less_than_or_equal(local_vc, final_vc):
                del self.order_data[order_id]  # Delete data FIRST
                print(f"Fraud Detection: Cleared data for order {order_id}")
                local_vc["fraud_detection"] = local_vc.get("fraud_detection", 0) + 1 #increment local clock
                return fraud_detection.ClearDataResponse(success=True)
            else:
                print(f"Fraud Detection: Vector clock mismatch for order {order_id}. Data not cleared.")
                return fraud_detection.ClearDataResponse(success=False)
        else:
            return fraud_detection.ClearDataResponse(success=True) #if order id is not in the stored data, it is already cleared


    def update_vector_clock(self, order_id, received_vc):
        local_vc = self.order_data[order_id]["vector_clock"]
        for key, value in received_vc.items():
            local_vc[key] = max(local_vc.get(key, 0), value)
        local_vc["fraud_detection"] = local_vc.get("fraud_detection", 0) + 1

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