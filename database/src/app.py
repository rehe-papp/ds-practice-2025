import sys
import os
import threading
import time

FILE = __file__ if '__file__' in globals() else os.getenv("PYTHONFILE", "")
utils_path_1 = os.path.abspath(os.path.join(FILE, '../../../utils/pb/database'))
sys.path.insert(0, utils_path_1)
import database_pb2 as database
import database_pb2_grpc as database_grpc


import grpc
from concurrent import futures


class DatabaseService(database_grpc.DatabaseServiceServicer):
    def __init__(self, database_id, known_ids):
        #where we store the shop items
        self.store = {}
        self.initialize_book_stock()

        self.database_id = database_id
        self.known_ids = known_ids
        self.current_leader_id = None

        self.lock = threading.Lock()
        self.peer_stubs = {
            peer_id: database_grpc.DatabaseServiceStub(grpc.insecure_channel(addr))
            for peer_id, addr in known_ids.items() if peer_id != self.database_id
        }
        self.heartbeat_interval = 2
        self.leader_timeout = 5
        self.last_heartbeat = time.time()

        #So first election is done before we start monitoring heartbeat
        #self.election_complete = threading.Event()

        # Start initial election immediately
        #threading.Thread(target=self.start_initial_election, daemon=True).start()
        # Start heartbeat monitoring in separate thread
        threading.Thread(target=self.monitor_heartbeat, daemon=True).start()

    
    def Read(self, request, context):
        with self.lock:
            entry = self.store.get(request.title)
            if entry:
                stock = entry["stock"]
                timestamp = entry["timestamp"]
            else:
                stock = 0
                timestamp = 0
        return database.ReadResponse(stock=stock, timestamp=timestamp)


    def Write(self, request, context):
        is_forwarded = dict(context.invocation_metadata()).get('forwarded') == 'true'

        with self.lock:
        # Always write to local store first
            
            self.store[request.title] = {
                "stock": request.new_stock,
                "timestamp": request.timestamp
            }
        print(f"Successfully written in replica {self.database_id}")
        if self.database_id != self.current_leader_id:
            if not is_forwarded:
                try:
                    leader_stub = self.peer_stubs[self.current_leader_id]
                    leader_stub.Write(request, metadata=(('forwarded', 'true'),))
                    return database.WriteResponse(success=True)
                except grpc.RpcError:
                    context.set_code(grpc.StatusCode.UNAVAILABLE)
                    context.set_details("Could not reach leader")
                    return database.WriteResponse(success=False)
        else:
            ack_count = 0
            for peer_id, stub in self.peer_stubs.items():
                try:
                    stub.Write(request, metadata=(('forwarded', 'true'),))
                    ack_count += 1
                except grpc.RpcError:
                    continue

            return database.WriteResponse(success=(ack_count >= 1))
    

    def SendHeartbeat(self, request, context):
        self.last_heartbeat = time.time()
        return database.HeartbeatResponse(alive=True)


    def StartElection(self, request, context):
        print(f"Received election from Node {request.from_database_id}")
        return database.ElectionResponse(acknowledged=True)


    def AnnounceLeader(self, request, context):
        new_leader = request.new_leader_id
        self.current_leader_id = new_leader
        print(f"Node {self.database_id} acknowledges new leader: Node {new_leader}")
        return database.Empty()
    
    def start_leader_election(self):
        print(f"[{self.database_id}] Starting leader election...")
        higher_ids = [eid for eid in self.known_ids if eid > self.database_id]
        received_ack = False

        for hid in higher_ids:
            try:
                with grpc.insecure_channel(self.known_ids[hid]) as channel:
                    stub = database_grpc.DatabaseServiceStub(channel)
                    response = stub.StartElection(database.ElectionRequest(
                        from_database_id=self.database_id
                    ))
                    if response.acknowledged:
                        received_ack = True
            except Exception as e:
                print(f"[{self.database_id}] No response from {hid}: {e}")

        if not received_ack:
            print(f"[{self.database_id}] No higher ID responded. Becoming leader.")
            self.current_leader_id = self.database_id
            self.announce_leadership()
        else:
            print(f"[{self.database_id}] Higher ID exists. Waiting for leader announcement...")

    
    def announce_leadership(self):
        for eid, addr in self.known_ids.items():
            if eid == self.database_id:
                continue
            try:
                with grpc.insecure_channel(addr) as channel:
                    stub = database_grpc.DatabaseServiceStub(channel)
                    stub.AnnounceLeader(database.CoordinatorMessage(new_leader_id=self.database_id))
            except Exception as e:
                print(f"[{self.database_id}] Failed to announce leader to {eid}: {e}")


    def monitor_heartbeat(self):
        time.sleep(3 * self.database_id)
        self.start_leader_election()

        while True:
            time.sleep(self.heartbeat_interval)

            if self.database_id==self.current_leader_id:
                continue  # Leader doesn't check heartbeats

            if self.current_leader_id is None:
                for peer_id, stub in self.peer_stubs.items():
                    try:
                        response = stub.SendHeartbeat(database.HeartbeatRequest(from_database_id=self.database_id))
                        if response.alive:
                            self.current_leader_id = peer_id
                            print(f"Node {self.database_id} found leader Node {peer_id} on startup")
                            break
                    except grpc.RpcError:
                        print("error")
                        continue

                if self.current_leader_id is None:
                    self.start_leader_election()
            else:
                try:
                    stub = self.peer_stubs[self.current_leader_id]
                    stub.SendHeartbeat(database.HeartbeatRequest(from_database_id=self.database_id))
                except grpc.RpcError:
                    print(f"Node {self.database_id} detected leader {self.current_leader_id} is down")
                    self.current_leader_id = None
                    self.start_leader_election()


    
    def initialize_book_stock(self):
        books_data = {
            "Learning Python": {"stock": 7, "timestamp": int(time.time())},
            "JavaScript - The Good Parts": {"stock": 15, "timestamp": int(time.time())},
            "Domain-Driven Design: Tackling Complexity in the Heart of Software": {"stock": 15, "timestamp": int(time.time())},
            "Design Patterns: Elements of Reusable Object-Oriented Software": {"stock": 15, "timestamp": int(time.time())},
        }
        self.store.update(books_data)
        print("Book store initialized:", self.store)




def serve_database_service(database_id, known_ids, port):
    # Create a gRPC server
    server = grpc.server(futures.ThreadPoolExecutor())
    # Add
    service = DatabaseService(database_id, known_ids)
    database_grpc.add_DatabaseServiceServicer_to_server(service, server)
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
        1: "database1:50058",
        2: "database2:50059",
        3: "database3:50060",
    }
    serve_database_service(database_id, known, port)