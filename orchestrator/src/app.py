import sys
import os
from concurrent.futures import ThreadPoolExecutor

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

import fraud_detection_pb2 as fraud_detection
import fraud_detection_pb2_grpc as fraud_detection_grpc
import transaction_verification_pb2 as transaction_verification
import transaction_verification_pb2_grpc as transaction_verification_grpc
import suggestions_pb2 as suggestions
import suggestions_pb2_grpc as suggestions_grpc

import grpc

def DetectFraud(request_data):
    with grpc.insecure_channel('fraud_detection:50051') as channel:
        # Create a stub object
        stub = fraud_detection_grpc.FraudDetectionServiceStub(channel)

        user = request_data.get('user', {})
        credit_card = request_data.get('creditCard', {})
        items = request_data.get('items', [])
        billing_address = request_data.get('billingAddress', {})
        user_comment = request_data.get('userComment', "")
        shipping_method = request_data.get('shippingMethod', "")
        gift_wrapping = request_data.get('giftWrapping', False)
        terms_accepted = request_data.get('termsAccepted', False)


        # Convert items list to protobuf format
        item_list = [fraud_detection.Item(bookid=item["bookid"], quantity=item["quantity"]) for item in items]

        # Construct the FraudRequest message
        request = fraud_detection.FraudRequest(
            user=fraud_detection.User(
                name=user["name"],
                contact=user["contact"]
            ),
            creditCard=fraud_detection.CreditCard(
                number=credit_card["number"],
                expirationDate=credit_card["expirationDate"],
                cvv=credit_card["cvv"]
            ),
            userComment=user_comment,
            items=item_list,
            billingAddress=fraud_detection.Address(
                street=billing_address["street"],
                city=billing_address["city"],
                state=billing_address["state"],
                zip=billing_address["zip"],
                country=billing_address["country"]
            ),
            shippingMethod=shipping_method,
            giftWrapping=gift_wrapping,
            termsAccepted=terms_accepted
        )

        # Call the gRPC service
        response = stub.FraudDetection(request)
    return response


def VerifyTransaction(request_data):
    with grpc.insecure_channel('transaction_verification:50052') as channel:
        # Create a stub object
        stub = transaction_verification_grpc.TransactionVerificationServiceStub(channel)

        # Construct the gRPC request
        transaction_request = transaction_verification.TransactionVerificationRequest(
            user=transaction_verification.User(
                name=request_data.get('user', {}).get('name', ""),
                contact=request_data.get('user', {}).get('contact', "")
            ),
            creditCard=transaction_verification.CreditCard(
                number=request_data.get('creditCard', {}).get('number', ""),
                expirationDate=request_data.get('creditCard', {}).get('expirationDate', ""),
                cvv=request_data.get('creditCard', {}).get('cvv', "")
            ),
            userComment=request_data.get('userComment', ""),
            items=[
                transaction_verification.Item(
                    bookid=item.get('bookid', ""),
                    quantity=item.get('quantity', 0)
                ) for item in request_data.get('items', [])
            ],
            billingAddress=transaction_verification.Address(
                street=request_data.get('billingAddress', {}).get('street', ""),
                city=request_data.get('billingAddress', {}).get('city', ""),
                state=request_data.get('billingAddress', {}).get('state', ""),
                zip=request_data.get('billingAddress', {}).get('zip', ""),
                country=request_data.get('billingAddress', {}).get('country', "")
            ),
            shippingMethod=request_data.get('shippingMethod', ""),
            termsAccepted=request_data.get('termsAccepted', False)
        )

        # Call the service and get the response
        response = stub.VerifyTransaction(transaction_request)

    return response

def GetSuggestions(book_ids):
    with grpc.insecure_channel('suggestions:50053') as channel:
        stub = suggestions_grpc.SuggestionsServiceStub(channel) #use stub
        response = stub.SuggestBooks(suggestions.SuggestBooksRequest(bookID=book_ids))
    return response.suggestions #return the list of suggestions.


# Import Flask.
# Flask is a web framework for Python.
# It allows you to build a web application quickly.
# For more information, see https://flask.palletsprojects.com/en/latest/
from flask import Flask, request
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
    """
    Responds with a JSON object containing the order ID, status, and suggested books.
    """
    # Get request object data to json
    request_data = json.loads(request.data)
    # Print request object data
    print("Request Data:", request_data.get('items'))
    #print(request_data)

    items = request_data.get('items', [])

    # Dummy response following the provided YAML specification for the bookstore

    book_ids = []
    for item in items:
        bookid = item.get('bookid')
        try:
            if bookid is not None:
                book_ids.append(int(bookid))
        except ValueError:
            print(f"Warning: bookid '{bookid}' not an integer")

    #spawn new threads for each microservice
    # in each thread call the microservice and get the response
    # join the threads
    #decide if order approved or rejected
    #return response

    
    try:
        with ThreadPoolExecutor(max_workers=3) as executor:
            print("Starting threads")
            # Submit tasks to the thread pool
            future_1 = executor.submit(DetectFraud, request_data)
            future_2 = executor.submit(VerifyTransaction, request_data)
            future_3 = executor.submit(GetSuggestions, book_ids)
            
            # Wait for all tasks to complete
            fraud_response = future_1.result()
            transaction_verification_response = future_2.result()
            suggested_books = future_3.result()
    except Exception as e:
        print(e)
        return {"error": {"code": "500","message": "Internal Server Error"}}, 500

    suggested_books_list = []
    for book in suggested_books:
        suggested_books_list.append({'bookid': book.bookID, 'title': book.title, 'author': book.author})

    if transaction_verification_response.is_valid and fraud_response.is_valid:
        order_status_response = {
        'orderId': '12345',
        'status': 'Order Approved',
        'suggestedBooks': suggested_books_list
        }
    else:
        order_status_response = {
        'orderId': '12345',
        'status': "Order Rejected",
        'suggestedBooks': suggested_books_list
        }

    return order_status_response


if __name__ == '__main__':
    # Run the app in debug mode to enable hot reloading.
    # This is useful for development.
    # The default port is 5000.
    app.run(host='0.0.0.0')
