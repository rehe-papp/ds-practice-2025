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

FILE = __file__ if '__file__' in globals() else os.getenv("PYTHONFILE", "")
utils_path_3 = os.path.abspath(os.path.join(FILE, '../../../utils/pb/payment_service'))
sys.path.insert(0, utils_path_3)
import payment_service_pb2 as payment
import payment_service_pb2_grpc as payment_grpc

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

        self.payment_stub = payment_grpc.PaymentServiceStub(grpc.insecure_channel('payment_service:50061'))

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
    
    
    def _perform_quorum_write_for_item(self, title, quantity, read_responses):
         """
         Performs the original quorum write logic for a single item.
         This method is kept to demonstrate the previous task's functionality,
         but is not used in the primary 2PC order processing flow.
         Returns True if write quorum is achieved, False otherwise.
         """
         # Calculate new stock based on the latest read (from the quorum read phase)
         # Ensure title exists in read_responses before accessing
         if title not in read_responses:
              print(f"[{self.executor_id}] Error: Title '{title}' not found in read_responses for quorum write.")
              return False # Cannot perform write if read failed for this item

         latest_stock = read_responses[title][0]
         new_stock = latest_stock - quantity
         new_timestamp = int(time.time())
         ack_count = 0

         print(f"[{self.executor_id}] Attempting quorum write for '{title}' with new stock {new_stock}")

         for db_id, stub in self.database_stubs.items():
             try:
                 # Use the original Write RPC on the database
                 write_resp = stub.Write(database.WriteRequest(
                      title=title,
                      new_stock=new_stock,
                      timestamp=new_timestamp
                 ), timeout=5) # Add a timeout

                 if write_resp.success:
                     ack_count += 1
                     print(f"[{self.executor_id}] Write acknowledged by DB {db_id} for '{title}'.")
             except grpc.RpcError as e:
                 print(f"[{self.executor_id}] RPC Error during quorum write to DB {db_id} for '{title}': {e}")
                 continue # Keep trying other replicas even if one fails
             except Exception as e:
                  print(f"[{self.executor_id}] An unexpected error occurred during quorum write to DB {db_id} for '{title}': {e}")
                  continue

         write_quorum_achieved = ack_count >= self.write_quorum
         if write_quorum_achieved:
              print(f"[{self.executor_id}] Write quorum ({self.write_quorum}) achieved for '{title}' ({ack_count} acks).")
         else:
              print(f"[{self.executor_id}] Write quorum ({self.write_quorum}) NOT achieved for '{title}' ({ack_count} acks).")

         return write_quorum_achieved


    def two_phase_commit(self, order):
        print(f"[{self.executor_id}] Starting 2PC for order {order.orderId}")

        # Participants: The Payment Service and ALL Database Service replicas
        participants = [("payment", self.payment_stub)] + [
            (f"database-{db_id}", stub) for db_id, stub in self.database_stubs.items()
        ]

        # Phase 1: Prepare
        all_ready = True
        # Data to be sent to database participants for Prepare
        database_item_updates = []
        for item in order.items:
            database_item_updates.append(database.DatabasePrepareRequest.ItemUpdate(
                title=item.title,
                quantity_change=-item.quantity # Stock decreases
            ))

        ready_votes = []
        for participant_name, stub in participants:
            try:
                if participant_name == "payment":
                    # Prepare request for Payment Service
                    # Need to calculate total amount for the order based on book prices
                    # For this simple example, let's use a dummy amount or calculate based on item quantity.
                    # Assuming each item has a price field in the order proto or you have price data locally.
                    # If price data is not available, you'd need to fetch it or include it in the order.
                    # Let's use a placeholder calculation for now.
                    dummy_total_amount = sum(item.quantity for item in order.items) * 10.0 # Example: $10 per book

                    prepare_request = payment.PrepareRequest(
                        order_id=order.orderId,
                        amount=dummy_total_amount # Send the calculated amount
                    )
                    # Add a timeout for the RPC call
                    response = stub.Prepare(prepare_request, timeout=5)
                    ready_votes.append(response.ready)
                    if not response.ready:
                        print(f"[{self.executor_id}] Participant {participant_name} voted NOT ready for order {order.orderId}")

                elif "database" in participant_name:
                    # Prepare request for Database Service replica
                    prepare_request = database.DatabasePrepareRequest(
                         order_id=order.orderId,
                         item_updates=database_item_updates # Send the list of item updates
                         )
                    # Add a timeout for the RPC call
                    response = stub.Prepare(prepare_request, timeout=5)
                    ready_votes.append(response.ready)
                    if not response.ready:
                        print(f"[{self.executor_id}] Participant {participant_name} voted NOT ready for order {order.orderId}")

                else:
                    # Unknown participant type
                    print(f"[{self.executor_id}] Unknown participant type: {participant_name}")
                    ready_votes.append(False)


            except grpc.RpcError as e:
                print(f"[{self.executor_id}] RPC Error during Prepare with {participant_name} for order {order.orderId}: {e}")
                ready_votes.append(False) # Consider RPC failure as a "not ready" vote
            except Exception as e:
                 print(f"[{self.executor_id}] An unexpected error occurred during Prepare with {participant_name}: {e}")
                 ready_votes.append(False) # Consider any exception as a "not ready" vote


        all_ready = all(ready_votes)


        # Phase 2: Commit or Abort
        if all_ready:
            print(f"[{self.executor_id}] All participants voted ready for order {order.orderId}. Sending Commit.")
            # Use a list to track commit successes, important for recovery in real 2PC
            commit_successes = []
            for participant_name, stub in participants:
                try:
                    if participant_name == "payment":
                        commit_request = payment.CommitRequest(order_id=order.orderId)
                        # Add a timeout for the RPC call
                        commit_resp = stub.Commit(commit_request, timeout=5)
                        commit_successes.append((participant_name, commit_resp.success))
                        print(f"[{self.executor_id}] Sent Commit to {participant_name} for order {order.orderId}, Success: {commit_resp.success}")
                    elif "database" in participant_name:
                        commit_request = database.DatabaseCommitRequest(order_id=order.orderId)
                        # Add a timeout for the RPC call
                        commit_resp = stub.Commit(commit_request, timeout=5)
                        commit_successes.append((participant_name, commit_resp.success))
                        print(f"[{self.executor_id}] Sent Commit to {participant_name} for order {order.orderId}, Success: {commit_resp.success}")
                except grpc.RpcError as e:
                    print(f"[{self.executor_id}] RPC Error during Commit with {participant_name} for order {order.orderId}: {e}")
                    commit_successes.append((participant_name, False)) # RPC error means commit failed or state is uncertain
                except Exception as e:
                     print(f"[{self.executor_id}] An unexpected error occurred during Commit with {participant_name}: {e}")
                     commit_successes.append((participant_name, False))

            # In a real 2PC, the coordinator must log the outcome and handle failures during commit.
            # For this simple implementation, we'll assume success if Prepare was successful.
            # A more robust check would be if ALL commit responses were successful,
            # but RPC failures during commit lead to the indeterminable state.
            transaction_fully_committed = all(success for name, success in commit_successes)
            print(f"[{self.executor_id}] 2PC Commit phase completed for order {order.orderId}. Fully Committed: {transaction_fully_committed}")
            return transaction_fully_committed # Indicate success only if all commits were reported successful

        else:
            print(f"[{self.executor_id}] One or more participants not ready for order {order.orderId}. Sending Abort.")
            # Abort is typically best-effort
            for participant_name, stub in participants:
                try:
                    if participant_name == "payment":
                         abort_request = payment.AbortRequest(order_id=order.orderId)
                         # Add a timeout for the RPC call
                         stub.Abort(abort_request, timeout=5)
                         print(f"[{self.executor_id}] Sent Abort to {participant_name} for order {order.orderId}")
                    elif "database" in participant_name:
                         abort_request = database.DatabaseAbortRequest(order_id=order.orderId)
                         # Add a timeout for the RPC call
                         stub.Abort(abort_request, timeout=5)
                         print(f"[{self.executor_id}] Sent Abort to {participant_name} for order {order.orderId}")
                except grpc.RpcError as e:
                    print(f"[{self.executor_id}] RPC Error during Abort with {participant_name} for order {order.orderId}: {e}")
                    # Log errors during abort, but typically proceed.
                except Exception as e:
                     print(f"[{self.executor_id}] An unexpected error occurred during Abort with {participant_name}: {e}")


            print(f"[{self.executor_id}] 2PC Abort phase completed for order {order.orderId}")
            return False # Indicate failed processing of the transaction



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
                        all_items_readable_by_quorum = True
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
                                all_items_readable_by_quorum = False
                                break

                            # Find the state with the latest timestamp among the responses
                            if item_responses:
                                # Sort by timestamp, most recent first
                                item_responses.sort(key=lambda x: x[1], reverse=True)
                                latest_stock, latest_ts = item_responses[0]
                                read_responses[title] = (latest_stock, latest_ts) # Store latest in your original structure
                            else:
                                # No responses received for this item
                                print(f"[{self.executor_id}] No valid read responses received for book '{title}'. Skipping order.")
                                all_items_readable_by_quorum = False
                                break

                        if not all_items_readable_by_quorum:
                            continue 

                        all_valid = True
                        for title, (stock, quantity_needed) in read_responses.items(): # Iterate through items that had successful quorum reads
                                # Get the quantity needed from the original order object
                                current_item = next((item for item in order.items if item.title == title), None)
                                if current_item is None:
                                     # Should not happen if all_items_readable_by_quorum is True and titles match
                                     print(f"[{self.executor_id}] Internal error: Item title '{title}' from read_responses not found in original order items.")
                                     all_valid = False
                                     break

                                quantity_needed = current_item.quantity


                                if stock < quantity_needed:
                                    print(f"[{self.executor_id}] Not enough stock based on latest read for '{title}' (Needed: {quantity_needed}, Available: {stock}). Skipping order {order.orderId}.")
                                    all_valid = False
                                    break
                            
                        
                        if not all_valid:
                            continue  # Skip this order if any book doesn't have enough stock
                        
                        # Step 3: Write to replicas, require quorum
                        
                        # --- Integrate Two-Phase Commit for Order Processing (NEW Logic - REPLACE QUORUM WRITE) ---
                        # This replaces the original direct quorum write loop for order fulfillment.
                        print(f"[{self.executor_id}] Initial read check passed. Proceeding with 2PC transaction.")
                        transaction_successful = self.two_phase_commit(order) # Call the new 2PC method

                        if transaction_successful:
                            print(f"[{self.executor_id}] Successfully processed order {order.orderId} via 2PC.")
                        else:
                            print(f"[{self.executor_id}] Failed to process order {order.orderId} via 2PC.")
                            # Depending on requirements, you might re-enqueue the order, log it, etc.
                            # Be cautious with re-enqueueing failed 2PC transactions without
                            # robust idempotency or compensation logic.
                                


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

