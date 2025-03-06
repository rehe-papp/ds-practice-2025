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
    # Create an RPC function to say hello
    def SuggestBooks(self, request, context):
        book_ids = request.bookID  # Access the repeated field
        print(f"Received request for suggestions for book IDs: {book_ids}")

        book_data = [
            {"bookID": 4,"title": "The Example Book", "author": "John Doe"},
            {"bookID": 5, "title": "Another Book", "author": "Jane Smith"},
        ]
        

        all_suggestions = []
        for book in book_data:
            all_suggestions.append(suggestions.BookSuggestion(bookID=book["bookID"], title=book["title"], author=book["author"]))


        response = suggestions.SuggestionsResponse()
        response.suggestions.extend(all_suggestions)

        print(f"Suggestions response: {response}")

        return response



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