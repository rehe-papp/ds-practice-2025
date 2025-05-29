from locust import HttpUser, task
from locust.exception import StopUser

class nonFraudulent(HttpUser):
    host = "http://localhost:8081" 

    def on_start(self):
        self.order_a()
        self.order_b()
        raise StopUser()

    
    def order_a(self):
        order_data = {
            'user': {'name': 'John Doe', 'contact': 'john.doe@example.com'}, 
            'creditCard': {'number': '4111111111111111', 'expirationDate': '12/25', 'cvv': '123'}, 
            'userComment': 'Please handle with care.', 
            'items': [{'bookid': 1, 'quantity': 2, 'title': 'Learning Python', 'author': 'Example1'}, 
                   {'bookid': 2, 'quantity': 2, 'title': 'JavaScript - The Good Parts', 'author': 'Example2'}], 
            'billingAddress': {'street': '123 Main St', 'city': 'Springfield', 'state': 'IL', 'zip': '62701', 'country': 'USA'}, 
            'shippingMethod': 'Standard', 'giftWrapping': True, 'termsAccepted': True
        }
        self.client.post("/checkout", json=order_data)

    
    def order_b(self):
        order_data = {
            'user': {'name': 'Jane Doe', 'contact': 'jane.doe@example.com'}, 
            'creditCard': {'number': '4111111111111101', 'expirationDate': '12/24', 'cvv': '321'}, 
            'userComment': 'Please handle with care.', 
            'items': [{'bookid': 3, 'quantity': 2, 'title': 'Domain-Driven Design: Tackling Complexity in the Heart of Software', 'author': 'Example1'}, 
                   {'bookid': 4, 'quantity': 2, 'title': 'Design Patterns: Elements of Reusable Object-Oriented Software', 'author': 'Example2'}], 
            'billingAddress': {'street': '321 Main St', 'city': 'Springfield', 'state': 'IL', 'zip': '62701', 'country': 'USA'}, 
            'shippingMethod': 'Standard', 'giftWrapping': True, 'termsAccepted': True
        }
        self.client.post("/checkout", json=order_data)

class Mixed(HttpUser):
    host = "http://localhost:8081" 

    def on_start(self):
        self.order_a()
        self.order_b()
        self.order_c()
        raise StopUser()

    
    def order_a(self):
        order_data = {
            'user': {'name': 'John Doe', 'contact': 'john.doe@example.com'}, 
            'creditCard': {'number': '0000111111111111', 'expirationDate': '12/25', 'cvv': '123'}, 
            'userComment': 'Please handle with care.', 
            'items': [{'bookid': 1, 'quantity': 2, 'title': 'Learning Python', 'author': 'Example1'}, 
                   {'bookid': 2, 'quantity': 2, 'title': 'JavaScript - The Good Parts', 'author': 'Example2'}], 
            'billingAddress': {'street': '123 Main St', 'city': 'Springfield', 'state': 'IL', 'zip': '62701', 'country': 'USA'}, 
            'shippingMethod': 'Standard', 'giftWrapping': True, 'termsAccepted': True
        }
        self.client.post("/checkout", json=order_data)

    
    def order_b(self):
        order_data = {
            'user': {'name': 'Jane Doe', 'contact': 'jane.doe@example.com'}, 
            'creditCard': {'number': '4111111111111101', 'expirationDate': '12/24', 'cvv': '321'}, 
            'userComment': 'Please handle with care.', 
            'items': [{'bookid': 3, 'quantity': 2, 'title': 'Domain-Driven Design: Tackling Complexity in the Heart of Software', 'author': 'Example1'}], 
            'billingAddress': {'street': '321 Main St', 'city': 'Springfield', 'state': 'IL', 'zip': '62701', 'country': 'USA'}, 
            'shippingMethod': 'Standard', 'giftWrapping': True, 'termsAccepted': True
        }
        self.client.post("/checkout", json=order_data)

    
    def order_c(self):
        order_data = {
            'user': {'name': 'Jane Smith', 'contact': 'jane.smith@example.com'}, 
            'creditCard': {'number': '4111111111111101', 'expirationDate': '12/24', 'cvv': '321'}, 
            'userComment': 'Please handle with care.', 
            'items': [{'bookid': 4, 'quantity': 200, 'title': 'Design Patterns: Elements of Reusable Object-Oriented Software', 'author': 'Example1'}], 
            'billingAddress': {'street': '321 Main St', 'city': 'Springfield', 'state': 'IL', 'zip': '62701', 'country': 'USA'}, 
            'shippingMethod': 'Standard', 'giftWrapping': True, 'termsAccepted': True
        }
        self.client.post("/checkout", json=order_data)

class Conflicting(HttpUser):
    host = "http://localhost:8081" 

    def on_start(self):
        self.order_a()
        self.order_b()
        raise StopUser()

    
    def order_a(self):
        order_data = {
            'user': {'name': 'John Doe', 'contact': 'john.doe@example.com'}, 
            'creditCard': {'number': '0000111111111111', 'expirationDate': '12/25', 'cvv': '123'}, 
            'userComment': 'Please handle with care.', 
            'items': [{'bookid': 1, 'quantity': 2, 'title': 'Learning Python', 'author': 'Example1'}, 
                   {'bookid': 2, 'quantity': 2, 'title': 'JavaScript - The Good Parts', 'author': 'Example2'}], 
            'billingAddress': {'street': '123 Main St', 'city': 'Springfield', 'state': 'IL', 'zip': '62701', 'country': 'USA'}, 
            'shippingMethod': 'Standard', 'giftWrapping': True, 'termsAccepted': True
        }
        self.client.post("/checkout", json=order_data)

    
    def order_b(self):
        order_data = {
            'user': {'name': 'Jane Doe', 'contact': 'jane.doe@example.com'}, 
            'creditCard': {'number': '4111111111111101', 'expirationDate': '12/24', 'cvv': '321'}, 
            'userComment': 'Please handle with care.', 
            'items': [{'bookid': 2, 'quantity': 2, 'title': 'JavaScript - The Good Parts', 'author': 'Example2'}, 
                   {'bookid': 4, 'quantity': 2, 'title': 'Design Patterns: Elements of Reusable Object-Oriented Software', 'author': 'Example2'}], 
            'billingAddress': {'street': '321 Main St', 'city': 'Springfield', 'state': 'IL', 'zip': '62701', 'country': 'USA'}, 
            'shippingMethod': 'Standard', 'giftWrapping': True, 'termsAccepted': True
        }
        self.client.post("/checkout", json=order_data)