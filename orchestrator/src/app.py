import sys
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import uuid
import json
import random
import traceback
import time


from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from opentelemetry import metrics
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader

# This set of lines are needed to import the gRPC stubs.
# The path of the stubs is relative to the current file, or absolute inside the container.
# Change these lines only if strictly needed.
FILE = __file__ if '__file__' in globals() else os.getenv("PYTHONFILE", "")
fraud_detection_grpc_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb/fraud_detection'))
sys.path.insert(0, fraud_detection_grpc_path)
transaction_verification_grpc_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb/transaction_verification'))
sys.path.insert(0, transaction_verification_grpc_path)
suggestions_grpc_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb/suggestions'))
sys.path.insert(0, suggestions_grpc_path)
order_queue_grpc_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb/order_queue'))
sys.path.insert(0, order_queue_grpc_path)

import fraud_detection_pb2 as fraud_detection
import fraud_detection_pb2_grpc as fraud_detection_grpc
import transaction_verification_pb2 as transaction_verification
import transaction_verification_pb2_grpc as transaction_verification_grpc
import suggestions_pb2 as suggestions
import suggestions_pb2_grpc as suggestions_grpc
import order_queue_pb2 as order_queue
import order_queue_pb2_grpc as order_queue_grpc

import grpc


resource = Resource(attributes={
    SERVICE_NAME: "orchestrator"
})

traceProvider = TracerProvider(resource=resource)
processor = BatchSpanProcessor(OTLPSpanExporter(endpoint="http://observability:4318/v1/traces"))
traceProvider.add_span_processor(processor)
trace.set_tracer_provider(traceProvider)

reader = PeriodicExportingMetricReader(
    OTLPMetricExporter(endpoint="http://observability:4318/v1/metrics"),
)
meterProvider = MeterProvider(resource=resource, metric_readers=[reader])
metrics.set_meter_provider(meterProvider)

tracer = trace.get_tracer("orchestrator.tracer")
meter = metrics.get_meter("orchestrator.meter")

order_counter = meter.create_counter(
    "total_orders", description="The number of orders", unit="1"
)

fraud_success_counter = meter.create_counter("fraud_success_count")
fraud_failure_counter = meter.create_counter("fraud_failure_count")

verification_success_counter = meter.create_counter("verification_success_count")
verification_failure_counter = meter.create_counter("verification_failure_count")

suggestion_success_counter = meter.create_counter("suggestion_success_count")
suggestion_failure_counter = meter.create_counter("suggestion_failure_count")

enqueue_success_counter = meter.create_counter("enqueue_success_count")
enqueue_failure_counter = meter.create_counter("enqueue_failure_count")


checkout_duration = meter.create_histogram(
    "checkout_duration_ms",
    unit="ms",
    description="Time taken to process a checkout"
)



def enqueue_order(order_id, order_data):
    with tracer.start_as_current_span("enqueue_order_internal"):
        # Connects to order queue service and sends the data to queue
        print(f"Enqueueing order: {order_id}")
        try:
            with grpc.insecure_channel('order_queue:50054') as channel:
                stub = order_queue_grpc.OrderQueueServiceStub(channel)

                # Create list of BookItem messages
                items = [
                    order_queue.BookItem(title=item["title"], quantity=item["quantity"])
                    for item in order_data["items"]
                ]

                order_message = order_queue.Order(
                    orderId=order_id,
                    userName=order_data['user']['name'],
                    items=items)
                response = stub.Enqueue(order_queue.EnqueueRequest(order=order_message))
                enqueue_success_counter.add(1, {"service": "order_queue"})
                print(f"Order enqueued: {response}")
                
        except Exception as e:
            print(f"ERROR: Exception in enqueue_order: {e}")
            enqueue_failure_counter.add(1, {"service": "order_queue"})
            return {"error": {"code": "500","message": "Internal Server Error"}}, 500
        return response

    
def initialize_fraud(order_id, request_data, vector_clock):
    with tracer.start_as_current_span("initialize_fraud"):
        with grpc.insecure_channel('fraud_detection:50051') as channel:
            stub = fraud_detection_grpc.FraudDetectionServiceStub(channel)

            user = fraud_detection.User(
                name=request_data.get('user', {}).get('name', ""),
                contact=request_data.get('user', {}).get('contact', "")
            )

            credit_card = fraud_detection.CreditCard(
                number=request_data.get('creditCard', {}).get('number', ""),
                expirationDate=request_data.get('creditCard', {}).get('expirationDate', ""),
                cvv=request_data.get('creditCard', {}).get('cvv', "")
            )

            items = [
                fraud_detection.Item(bookid=item.get('bookid', 0), quantity=item.get('quantity', 0))
                for item in request_data.get('items', [])
            ]

            billing_address = fraud_detection.Address(
                street=request_data.get('billingAddress', {}).get('street', ""),
                city=request_data.get('billingAddress', {}).get('city', ""),
                state=request_data.get('billingAddress', {}).get('state', ""),
                zip=request_data.get('billingAddress', {}).get('zip', ""),
                country=request_data.get('billingAddress', {}).get('country', "")
            )

            request = fraud_detection.FraudRequest(
                order_id=order_id,
                user=user,
                creditCard=credit_card,
                items=items,
                billingAddress=billing_address,
                userComment=request_data.get('userComment', ""),
                shippingMethod=request_data.get('shippingMethod', ""),
                giftWrapping=request_data.get('giftWrapping', False),
                termsAccepted=request_data.get('termsAccepted', False),
                vector_clock=fraud_detection.VectorClock(clock=vector_clock) #add vector clock
            )

            response = stub.InitializeFraud(request)
            return response
    
def process_fraud(order_id, vector_clock):
    with tracer.start_as_current_span("process_fraud_internal"):
        with grpc.insecure_channel('fraud_detection:50051') as channel:
            stub = fraud_detection_grpc.FraudDetectionServiceStub(channel)
            request = fraud_detection.ProcessFraudRequest(order_id=order_id, vector_clock=fraud_detection.VectorClock(clock=vector_clock))
            try:
                response = stub.ProcessFraud(request)
                fraud_success_counter.add(1, {"method": "ProcessFraud"})
                return response
            except Exception as e:
                fraud_failure_counter.add(1, {"method": "ProcessFraud"})
                raise
        raise

def initialize_verification(order_id, request_data, vector_clock):
    with tracer.start_as_current_span("initialize_verification"):
        with grpc.insecure_channel('transaction_verification:50052') as channel:
            stub = transaction_verification_grpc.TransactionVerificationServiceStub(channel)

            user = transaction_verification.User(
                name=request_data.get('user', {}).get('name', ""),
                contact=request_data.get('user', {}).get('contact', "")
            )

            credit_card = transaction_verification.CreditCard(
                number=request_data.get('creditCard', {}).get('number', ""),
                expirationDate=request_data.get('creditCard', {}).get('expirationDate', ""),
                cvv=request_data.get('creditCard', {}).get('cvv', "")
            )

            items = [
                transaction_verification.Item(bookid=item.get('bookid', 0), quantity=item.get('quantity', 0))
                for item in request_data.get('items', [])
            ]

            billing_address = transaction_verification.Address(
                street=request_data.get('billingAddress', {}).get('street', ""),
                city=request_data.get('billingAddress', {}).get('city', ""),
                state=request_data.get('billingAddress', {}).get('state', ""),
                zip=request_data.get('billingAddress', {}).get('zip', ""),
                country=request_data.get('billingAddress', {}).get('country', "")
            )

            request = transaction_verification.TransactionVerificationRequest(
                order_id=order_id,
                user=user,
                creditCard=credit_card,
                items=items,
                billingAddress=billing_address,
                userComment=request_data.get('userComment', ""),
                shippingMethod=request_data.get('shippingMethod', ""),
                termsAccepted=request_data.get('termsAccepted', False),
                vector_clock=transaction_verification.VectorClock(clock=vector_clock)
            )
            response = stub.InitializeVerification(request)
            return response

def process_verification(order_id, vector_clock, terms_accepted, items, user, credit_card, billing_address):
    with tracer.start_as_current_span("process_verification_internal"):
        print(f"Orchestrator - Credit Card Data being Sent: {credit_card}")

        with grpc.insecure_channel('transaction_verification:50052') as channel:
            stub = transaction_verification_grpc.TransactionVerificationServiceStub(channel)
            request = transaction_verification.ProcessVerificationRequest(
                order_id=order_id,
                vector_clock=transaction_verification.VectorClock(clock=vector_clock),
                termsAccepted=terms_accepted,
                items=items,
                user=user,
                creditCard=transaction_verification.CreditCard(
                    number=credit_card.get('number', ""),
                    expirationDate=credit_card.get('expirationDate', ""),
                    cvv=credit_card.get('cvv', "")
                ),
                billingAddress = transaction_verification.Address(
                    street = billing_address.get('street', ""),
                    city = billing_address.get('city', ""),
                    state = billing_address.get('state', ""),
                    zip = billing_address.get('zip', ""),
                    country = billing_address.get('country', "")
                )
            )
            try:
                response = stub.ProcessVerification(request)
                verification_success_counter.add(1, {"method": "ProcessVerification"})
                return response
            except Exception as e:
                verification_failure_counter.add(1, {"method": "ProcessVerification"})
                raise


def initialize_suggestions(order_id, book_ids, vector_clock):
    with tracer.start_as_current_span("initialize_suggestions"):
        with grpc.insecure_channel('suggestions:50053') as channel:
            stub = suggestions_grpc.SuggestionsServiceStub(channel)
            request = suggestions.SuggestBooksRequest(order_id=order_id, bookID=book_ids, vector_clock=suggestions.VectorClock(clock=vector_clock))
            response = stub.InitializeSuggestions(request)
            return response

def process_suggestions(order_id, vector_clock):
    with tracer.start_as_current_span("process_suggestions"):
        with grpc.insecure_channel('suggestions:50053') as channel:
            stub = suggestions_grpc.SuggestionsServiceStub(channel)
            request = suggestions.ProcessSuggestionsRequest(order_id=order_id, vector_clock=suggestions.VectorClock(clock=vector_clock))
            try: 
                response = stub.ProcessSuggestions(request)
                suggestion_success_counter.add(1, {"method": "ProcessSuggestions"})
                return response
            except:
                suggestion_failure_counter.add(1, {"method": "ProcessSuggestions"})
                raise

def broadcast_clear(order_id, final_vector_clock):
    with tracer.start_as_current_span("broadcast_clear"):
        print(f"Orchestrator - Before clear data: {final_vector_clock}")

        # Increment the orchestrator's vector clock component
        final_vector_clock['orchestrator'] = final_vector_clock.get('orchestrator', 0) + 1

        print(f"Orchestrator - After incrementing orchestrator clock: {final_vector_clock}")

        with grpc.insecure_channel('fraud_detection:50051') as channel:
            stub = fraud_detection_grpc.FraudDetectionServiceStub(channel)
            request = fraud_detection.ClearDataRequest(order_id=order_id, vector_clock=fraud_detection.VectorClock(clock=final_vector_clock))
            response = stub.ClearData(request)
            print(f"Orchestrator - fraud_detection clear data sent: {final_vector_clock}")

        with grpc.insecure_channel('transaction_verification:50052') as channel:
            stub = transaction_verification_grpc.TransactionVerificationServiceStub(channel)
            request = transaction_verification.ClearDataRequest(order_id=order_id, vector_clock=transaction_verification.VectorClock(clock=final_vector_clock))
            response = stub.ClearData(request)
            print(f"Orchestrator - transaction_verification clear data sent: {final_vector_clock}")

        with grpc.insecure_channel('suggestions:50053') as channel:
            stub = suggestions_grpc.SuggestionsServiceStub(channel)
            request = suggestions.ClearDataRequest(order_id=order_id, vector_clock=suggestions.VectorClock(clock=final_vector_clock))
            response = stub.ClearData(request)
            print(f"Orchestrator - suggestions clear data sent: {final_vector_clock}")

# Import Flask.
# Flask is a web framework for Python.
# It allows you to build a web application quickly.
# For more information, see https://flask.palletsprojects.com/en/latest/
from flask import Flask, request, jsonify
from flask_cors import CORS
import json

# Create a simple Flask app.
app = Flask(__name__)
# Enable CORS for the app.
CORS(app, resources={r'/*': {'origins': '*'}})

# Define a GET endpoint.
@app.route('/', methods=['GET'])
def index():
    """
    Responds with 'Hello, world!' when a GET request is made to '/' endpoint.
    """
    # Test the fraud-detection gRPC service.
    response = "Hello, world!"
    # Return the response.
    return response

@app.route('/checkout', methods=['POST'])

def checkout():
    start_time = time.time()
    with tracer.start_as_current_span("checkout") as span:
        request_data = json.loads(request.data)
        order_id = str(random.randint(0, 2**30-1))
        book_ids = [int(item.get('bookid')) for item in request_data.get('items', []) if item.get('bookid') is not None]
        vector_clock = {"orchestrator": 1, "fraud_detection": 0, "transaction_verification": 0, "suggestions": 0}
        
        span.set_attribute("order_id", order_id)
        span.set_attribute("book_ids.count", len(book_ids))

        try:
            with ThreadPoolExecutor(max_workers=3) as executor:
                futures = {
                    executor.submit(initialize_fraud, order_id, request_data, vector_clock.copy()): "fraud",
                    executor.submit(initialize_verification, order_id, request_data, vector_clock.copy()): "verification",
                    executor.submit(initialize_suggestions, order_id, book_ids, vector_clock.copy()): "suggestions",
                }
                for future in as_completed(futures):
                    result = future.result()
                    if result and hasattr(result, 'error') and result.error:
                        broadcast_clear(order_id, vector_clock.copy())
                        span.set_status(trace.Status(trace.StatusCode.ERROR, result.message))
                        return jsonify({"error": {"code": "500", "message": result.message}}), 500

            # Process Fraud
            
            fraud_result = process_fraud(order_id, vector_clock.copy())
            print(f"Orchestrator: After fraud processing, result: {fraud_result.is_valid}, message: {fraud_result.message}, vector_clock before update: {vector_clock}")
            vector_clock.update(fraud_result.vector_clock.clock)
            vector_clock["orchestrator"] += 1
            print(f"Orchestrator: After fraud update, vector_clock: {vector_clock}")

            # Check Fraud Result before proceeding to Verification
            if not fraud_result.is_valid:
                broadcast_clear(order_id, vector_clock)
                return jsonify({"error": {"code": "400", "message": f"Fraud check failed: {fraud_result.message}"}}), 400

            # Process Verification
            user_data = request_data.get('user')
            if user_data is None:
                broadcast_clear(order_id, vector_clock)
                return jsonify({"error": {"code": "400", "message": "Missing user information"}}), 400

            verification_result = process_verification(
                order_id,
                vector_clock,
                request_data.get('termsAccepted', False),
                request_data.get('items', []),
                user_data,
                request_data.get('creditCard', {}),
                request_data.get('billingAddress', {})
            )

            print(f"Orchestrator: After verification processing, result: {verification_result.is_valid}, message: {verification_result.message}, vector_clock before update: {vector_clock}")
            vector_clock.update(verification_result.vector_clock.clock)
            vector_clock["orchestrator"] += 1
            print(f"Orchestrator: After verification update, vector_clock: {vector_clock}")

            
            if verification_result.is_valid:
                queue_response = enqueue_order(int(order_id), request_data)
                print(f"{queue_response}")
            else:
                broadcast_clear(order_id, vector_clock)
                return jsonify({"error": {"code": "400", "message": verification_result.message}}), 400
            
            duration_ms = (time.time() - start_time) * 1000
            checkout_duration.record(duration_ms, {"status": "success"})    

            # Process Suggestions
            suggestions_result = process_suggestions(order_id, vector_clock.copy())
            vector_clock.update(suggestions_result.vector_clock.clock)
            vector_clock["orchestrator"] += 1
            print(f"Orchestrator: After suggestions processing, vector_clock: {vector_clock}")

            broadcast_clear(order_id, vector_clock.copy())
            suggested_books_list = [{'bookid': book.bookID, 'title': book.title, 'author': book.author} for book in suggestions_result.suggestions]
            return jsonify({'orderId': order_id, 'status': 'Order Approved', 'suggestedBooks': suggested_books_list})

        except grpc.RpcError as e:
            status_code = e.code()
            error_message = e.details()
            print(f"gRPC error: {status_code}, {error_message}")
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            checkout_duration.record(duration_ms, {"status": "success"})
            error_message = str(e)
            print(f"Unexpected error: {error_message}")
            traceback.print_exc()
            status_code = "500"
        return jsonify({"error": {"code": "500", "message": "Internal Server Error", "details": f"gRPC status: {status_code}, details: {error_message}"}}), 500


if __name__ == '__main__':
    # Run the app in debug mode to enable hot reloading.
    # This is useful for development.
    # The default port is 5000.
    app.run(host='0.0.0.0')
