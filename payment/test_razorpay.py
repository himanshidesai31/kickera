import razorpay
import json
import requests

# Razorpay API credentials
key_id = 'rzp_test_LiYIro0JdpKb1h'
key_secret = 'L9JB08EOR8kZ0ePmFjzNHwli'

def test_client_initialization():
    print("\n== Testing Client Initialization ==")
    try:
        client = razorpay.Client(auth=(key_id, key_secret))
        print("✓ Client initialized successfully")
        return client
    except Exception as e:
        print(f"✗ Client initialization failed: {str(e)}")
        return None

def test_order_creation(client):
    print("\n== Testing Order Creation ==")
    if not client:
        print("✗ Skipping test: Client not available")
        return
    
    try:
        # Basic order data with only required fields
        order_data = {
            'amount': 50000,  # ₹500
            'currency': 'INR',
            'receipt': 'receipt_test_123',
        }
        
        print(f"Creating order with data: {order_data}")
        order = client.order.create(order_data)
        print(f"✓ Order created successfully: {order['id']}")
        return order
    except Exception as e:
        print(f"✗ Order creation failed: {str(e)}")
        return None

def test_direct_api_call():
    print("\n== Testing Direct API Call (without SDK) ==")
    try:
        # Basic order data
        order_data = {
            'amount': 60000,  # ₹600
            'currency': 'INR',
            'receipt': 'receipt_direct_123',
        }
        
        # API endpoint
        url = 'https://api.razorpay.com/v1/orders'
        
        # Make the API call
        response = requests.post(
            url,
            auth=(key_id, key_secret),
            json=order_data
        )
        
        # Check the response
        if response.status_code == 200:
            order = response.json()
            print(f"✓ Direct API call successful: {order['id']}")
            return order
        else:
            print(f"✗ Direct API call failed with status {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print(f"✗ Direct API call exception: {str(e)}")
        return None

if __name__ == "__main__":
    print("=== Razorpay API Test ===")
    print(f"Using Key ID: {key_id[:4]}...{key_id[-4:]}")
    
    # Test client initialization
    client = test_client_initialization()
    
    # Test order creation using SDK
    test_order_creation(client)
    
    # Test direct API call without SDK
    test_direct_api_call() 