import sys
import os

# This set of lines are needed to import the gRPC stubs.
# The path of the stubs is relative to the current file, or absolute inside the container.
# Change these lines only if strictly needed.
FILE = __file__ if '__file__' in globals() else os.getenv("PYTHONFILE", "")
suggestions_grpc_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb/suggestions'))
sys.path.insert(0, suggestions_grpc_path)
import suggestions_pb2 as suggestions
import suggestions_pb2_grpc as suggestions_grpc

import grpc
from concurrent import futures

# Create a class to define the server functions, derived from
# suggestions_pb2_grpc.HelloServiceServicer
class SuggestionsService(suggestions_grpc.SuggestionsServiceServicer):
    def __init__(self):
        self.order_data = {}  # Store order data and vector clocks

    def InitializeSuggestions(self, request, context):
        order_id = request.order_id
        self.order_data[order_id] = {
            "request": request,
            "vector_clock": dict(request.vector_clock.clock)  # store vector clock as dict
        }
        print(f"Suggestions: Initialized order {order_id} with vector clock {self.order_data[order_id]['vector_clock']}")
        return suggestions.SuggestionsResponse(error=False)  # return a success response

    def ProcessSuggestions(self, request, context):
        order_id = request.order_id
        if order_id not in self.order_data:
            return suggestions.SuggestionsResponse(error=True, message="Order not initialized.")

        received_vc_from_orchestrator = dict(request.vector_clock.clock)
        print(f"Suggestions: Received ProcessSuggestions request for order {order_id} with vector clock from orchestrator: {received_vc_from_orchestrator}")

        local_vc = self.order_data[order_id]["vector_clock"]
        print(f"Suggestions: Local vector clock before processing: {local_vc}")

        fraud_processed = received_vc_from_orchestrator.get("fraud_detection", 0) > 1
        verification_processed = received_vc_from_orchestrator.get("transaction_verification", 0) > 1

        if not fraud_processed or not verification_processed:
            return suggestions.SuggestionsResponse(error=True, message="Waiting for Fraud Detection and Transaction Verification to complete.")

        book_data = [
            {"bookID": 4, "title": "The Example Book", "author": "John Doe"},
            {"bookID": 5, "title": "Another Book", "author": "Jane Smith"},
        ]

        # Update vector clock with received clock
        self.update_vector_clock(order_id, dict(request.vector_clock.clock))

        response = suggestions.SuggestionsResponse(error=False)

        # Simple suggestion logic (replace with your actual logic)
        all_suggestions = []
        for book in book_data:
            all_suggestions.append(suggestions.Book(bookID=book["bookID"], title=book["title"], author=book["author"]))

        response.suggestions.extend(all_suggestions)

        local_vc = self.order_data[order_id]["vector_clock"]
        local_vc["suggestions"] = local_vc.get("suggestions", 0) + 1
        print(f"Suggestions: check for return {local_vc}")

        
        # Increment suggestions's own clock before returning
        self.order_data[order_id]["vector_clock"]["suggestions"] = self.order_data[order_id]["vector_clock"].get("suggestions", 0) + 1
        response.vector_clock.clock.update(self.order_data[order_id]["vector_clock"])
        print(f"Suggestions: Processing order {order_id} with vector clock {self.order_data[order_id]['vector_clock']} (after processing)")
        return response

    def ClearData(self, request, context):
        order_id = request.order_id
        final_vc = dict(request.vector_clock.clock)
        if order_id in self.order_data:
            local_vc = self.order_data[order_id]["vector_clock"]
            if self.is_vector_clock_less_than_or_equal(local_vc, final_vc):
                del self.order_data[order_id]
                print(f"Suggestions: Cleared data for order {order_id}")
                local_vc["suggestions"] = local_vc.get("suggestions", 0) + 1 #increment local clock
                return suggestions.ClearDataResponse(success=True)
            else:
                print(f"Suggestions: Vector clock mismatch for order {order_id}. Data not cleared.")
                return suggestions.ClearDataResponse(success=False)
        else:
            return suggestions.ClearDataResponse(success=True)  # if order id is not in the stored data, it is already cleared

    def update_vector_clock(self, order_id, received_vc):
        local_vc = self.order_data[order_id]["vector_clock"]
        for key, value in received_vc.items():
            local_vc[key] = max(local_vc.get(key, 0), value)
        local_vc["suggestions"] = local_vc.get("suggestions", 0) + 1

    def is_vector_clock_less_than_or_equal(self, local_vc, final_vc):
        for key, value in local_vc.items():
            if key not in final_vc or value > final_vc.get(key, 0):
                return False
        return True

def serve():
    # Create a gRPC server
    server = grpc.server(futures.ThreadPoolExecutor())
    # Add HelloService
    suggestions_grpc.add_SuggestionsServiceServicer_to_server(SuggestionsService(), server)
    # Listen on port 50053
    port = "50053"
    server.add_insecure_port("[::]:" + port)
    # Start the server
    server.start()
    print("Server started. Listening on port 50053.")
    # Keep thread alive
    server.wait_for_termination()

if __name__ == '__main__':
    serve()