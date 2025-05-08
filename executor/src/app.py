import threading
import sys
import os
import time

FILE = __file__ if '__file__' in globals() else os.getenv("PYTHONFILE", "")
utils_path_1 = os.path.abspath(os.path.join(FILE, '../../../utils/pb/executor'))
sys.path.insert(0, utils_path_1)
import executor_pb2 as executor
import executor_pb2_grpc as executor_grpc


FILE = __file__ if '__file__' in globals() else os.getenv("PYTHONFILE", "")
utils_path_2 = os.path.abspath(os.path.join(FILE, '../../../utils/pb/order_queue'))
sys.path.insert(0, utils_path_2)
import order_queue_pb2 as order_queue
import order_queue_pb2_grpc as order_queue_grpc


FILE = __file__ if '__file__' in globals() else os.getenv("PYTHONFILE", "")
utils_path_3 = os.path.abspath(os.path.join(FILE, '../../../utils/pb/database'))
sys.path.insert(0, utils_path_3)
import database_pb2 as database
import database_pb2_grpc as database_grpc


import grpc
from concurrent import futures


class ExecutorService(executor_grpc.ExecutorServiceServicer):
    def __init__(self, executor_id, known_ids, queue_stub):
        self.executor_id = executor_id
        self.known_ids = known_ids # IDs of other executors
        self.queue_stub = queue_stub
        self.leader_id = None
        self.running = True


        db_addresses = {
            1: "database1:50058",
            2: "database2:50059",
            3: "database3:50060",
        }
        self.database_stubs = {
            db_id: database_grpc.DatabaseServiceStub(grpc.insecure_channel(addr))
            for db_id, addr in db_addresses.items()
        }

        num_replicas = len(self.database_stubs)
        self.read_quorum = (num_replicas // 2) + 1  # majority for reads
        self.write_quorum = (num_replicas // 2) + 1  # majority for writes

    def SendHeartbeat(self, request, context):
        return executor.HeartbeatResponse(alive=True)

    def StartElection(self, request, context):
        print(f"[{self.executor_id}] Received election message from {request.from_executor_id}")
        return executor.ElectionResponse(acknowledged=True)

    def AnnounceLeader(self, request, context):
        print(f"[{self.executor_id}] New leader is {request.new_leader_id}")
        self.leader_id = request.new_leader_id
        return executor.Empty()

    def start_grpc_server(self, port):
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        executor_grpc.add_ExecutorServiceServicer_to_server(self, server)
        server.add_insecure_port(f'[::]:{port}')
        server.start()
        print(f"[{self.executor_id}] gRPC server running on port {port}")
        return server

    
    
    def start_leader_election(self):
        print(f"[{self.executor_id}] Starting leader election...")
        higher_ids = [eid for eid in self.known_ids if eid > self.executor_id]
        received_ack = False

        for hid in higher_ids:
            try:
                with grpc.insecure_channel(self.known_ids[hid]) as channel:
                    stub = executor_grpc.ExecutorServiceStub(channel)
                    response = stub.StartElection(executor.ElectionRequest(
                        from_executor_id=self.executor_id
                    ))
                    if response.acknowledged:
                        received_ack = True
            except Exception as e:
                print(f"[{self.executor_id}] No response from {hid}: {e}")

        if not received_ack:
            print(f"[{self.executor_id}] No higher ID responded. Becoming leader.")
            self.leader_id = self.executor_id
            self.announce_leadership()
        else:
            print(f"[{self.executor_id}] Higher ID exists. Waiting for leader announcement...")

    def announce_leadership(self):
        for eid, addr in self.known_ids.items():
            if eid == self.executor_id:
                continue
            try:
                with grpc.insecure_channel(addr) as channel:
                    stub = executor_grpc.ExecutorServiceStub(channel)
                    stub.AnnounceLeader(executor.CoordinatorMessage(new_leader_id=self.executor_id))
            except Exception as e:
                print(f"[{self.executor_id}] Failed to announce leader to {eid}: {e}")

    def run(self):
        def main_loop():
            while self.running:
                if self.leader_id == self.executor_id:
                    # Simulate order dequeue + execution
                    response = self.queue_stub.Dequeue(order_queue.DequeueRequest(executor_id=self.executor_id))
                    if response.success:
                        order = response.order
                        print(f"[{self.executor_id}] Executing order {order.orderId}")

                        read_responses = {}
                        for item in order.items:
                            title = item.title
                            quantity = item.quantity

                            # Step 1: Quorum-based read from replicas
                            item_responses = []
                            for db_id, stub in self.database_stubs.items():
                                try:
                                    print("trying to read", title)
                                    resp = stub.Read(database.ReadRequest(title=title))
                                    item_responses.append((resp.stock, resp.timestamp))
                                except grpc.RpcError:
                                    continue
                                if len(item_responses) >= self.read_quorum:
                                    break

                            if len(item_responses) < self.read_quorum:
                                print(f"[{self.executor_id}] Read quorum not reached for book '{title}'. Skipping order.")
                                continue

                            # Sort by timestamp, most recent first
                            item_responses.sort(key=lambda x: x[1], reverse=True)
                            latest_stock, latest_ts = item_responses[0]
                            read_responses[title] = (latest_stock, quantity)

                        all_valid = True
                        for title, (stock, quantity) in read_responses.items():
                            if stock < quantity:
                                print(f"[{self.executor_id}] Not enough stock to fulfill order for '{title}'")
                                all_valid = False
                                break


                            
                        if not all_valid:
                            continue  # Skip this order if any book doesn't have enough stock
                        
                        # Step 3: Write to replicas, require quorum
                        
                        for item in order.items:
                            title = item.title
                            quantity = item.quantity
                            new_stock = read_responses[title][0] - quantity
                            new_timestamp = int(time.time())
                            ack_count = 0

                            for db_id, stub in self.database_stubs.items():
                                try:
                                    write_resp = stub.Write(database.WriteRequest(
                                        title=title,
                                        new_stock=new_stock,
                                        timestamp=new_timestamp
                                    ))
                                    if write_resp.success:
                                        ack_count += 1
                                except grpc.RpcError as e:
                                    print(f"[{self.executor_id}] Write failed on DB {db_id}: {e}")
                                if ack_count >= self.write_quorum:
                                    print("Write quorum achieved")
                                    break

                        if ack_count >= self.write_quorum:
                            print(f"[{self.executor_id}] Order {order.orderId} succeeded.")
                        else:
                            print(f"[{self.executor_id}] Order {order.orderId} failed. Only {ack_count} replicas acknowledged")
                    else:
                        print(f"[{self.executor_id}] I'm the leader. No orders in queue. On standby")
                    time.sleep(3)
                else:
                    # Optional: check heartbeat from leader
                    try:
                        leader_addr = self.known_ids.get(self.leader_id)
                        if leader_addr:
                            with grpc.insecure_channel(leader_addr) as channel:
                                stub = executor_grpc.ExecutorServiceStub(channel)
                                response = stub.SendHeartbeat(executor.HeartbeatRequest(
                                    from_executor_id=self.executor_id
                                ))
                                if not response.alive:
                                    raise Exception("Heartbeat failed")
                    except:
                        print(f"[{self.executor_id}] Leader down. Triggering re-election...")
                        self.start_leader_election()
                    time.sleep(2)

        threading.Thread(target=main_loop, daemon=True).start()

def launch_executor(executor_id, known_ids, port):
    queue_channel = grpc.insecure_channel('order_queue:50054')
    queue_stub = order_queue_grpc.OrderQueueServiceStub(queue_channel)
    time.sleep(5)

    svc = ExecutorService(executor_id, known_ids, queue_stub)
    grpc_server = svc.start_grpc_server(port)
    svc.start_leader_election()
    svc.run()
    grpc_server.wait_for_termination()


if __name__ == "__main__":
    executor_id = int(os.environ.get("EXECUTOR_ID", 1))
    port = os.environ.get("PORT", "50055")
    known = {
        1: "executor1:50055",
        2: "executor2:50056",
        3: "executor3:50057",
    }
    launch_executor(executor_id, known, port)

