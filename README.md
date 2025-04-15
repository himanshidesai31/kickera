# Kickera

Kickera is a Django-based e-commerce platform for footwear products.

## Features

- User authentication and registration
- Product catalog with categories
- Shopping cart functionality
- Wishlist support
- Order management
- Payment integration with Razorpay
- Seller/Vendor management

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/kamleshchaudhary012/kickera.git
   cd kickera
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Apply migrations:
   ```
   python manage.py migrate
   ```

5. Run the development server:
   ```
   python manage.py runserver
   ```

## Project Structure

- `product/` - Product management
- `orders/` - Order processing and tracking
- `users/` - User authentication and profiles
- `vendor/` - Seller management
- `templates/` - HTML templates

## License

This project is licensed under the MIT License. 