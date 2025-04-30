import sys
import os
import threading

FILE = __file__ if '__file__' in globals() else os.getenv("PYTHONFILE", "")
utils_path_1 = os.path.abspath(os.path.join(FILE, '../../../utils/pb/database'))
sys.path.insert(0, utils_path_1)
import database_pb2 as database
import database_pb2_grpc as database_grpc


import grpc
from concurrent import futures


class DatabaseService(database_grpc.DatabaseServiceServicer):
    def __init__(self):
        self.store = {}
    
    def Read(self, request, context):
        stock = self.store.get(request.title, 0)
        return database.ReadResponse(stock=stock)

    def Write(self, request, context):
        self.store[request.title] = request.new_stock
        return database.WriteResponse(success=True)
    



def serve_database_service(database_id, known_ids, port):
    # Create a gRPC server
    server = grpc.server(futures.ThreadPoolExecutor())
    # Add
    database_grpc.add_DatabaseServiceServicer_to_server(DatabaseService(), server)
    # Listen on port 
    server.add_insecure_port("[::]:" + port)
    # Start the server
    server.start()
    print(f"Server started. Listening on port {port}.")    
    server.wait_for_termination()

if __name__ == '__main__':
    database_id = int(os.environ.get("DATABASE_ID", 1))
    port = os.environ.get("PORT", "50058")
    known = {
        1: "executor1:50058",
        2: "executor2:50059",
        3: "executor3:50060",
    }
    serve_database_service(database_id, known, port)