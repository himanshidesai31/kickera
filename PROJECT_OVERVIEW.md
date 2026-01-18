# Kickera Shoes Store - Project Overview

## Project Description
Kickera is a full-featured e-commerce platform specializing in shoes, built using Django. The platform includes user authentication, product management, shopping cart functionality, payment processing, and order management.

## Project Structure
The project is organized into several Django apps, each handling specific functionality:

1. **core/** - Main application handling home page and basic site functionality
2. **users/** - User authentication and profile management
3. **product/** - Product catalog and shopping cart functionality
4. **vendor/** - Vendor/seller management system
5. **payment/** - Payment processing integration with Razorpay
6. **orders/** - Order management and tracking
7. **templates/** - HTML templates for the frontend
8. **static/** - Static files (CSS, JavaScript, images)
9. **media/** - User-uploaded media files

## Key Features

### Authentication System
- Email-based authentication using Django-Allauth
- User registration and login
- Password reset functionality
- Email verification
- Custom user model

### Product Management
- Product catalog
- Product categories
- Product search and filtering
- Shopping cart functionality
- Wishlist feature

### Payment Processing
- Integration with Razorpay payment gateway
- Secure payment processing
- Payment callback handling
- Order status tracking

### Order Management
- Order creation and tracking
- Order history
- Order status updates
- Invoice generation

### Vendor Management
- Vendor registration
- Product listing for vendors
- Order management for vendors
- Sales tracking

## Technical Stack

### Backend
- Django 3.2+
- SQLite database (development)
- Django-Allauth for authentication
- Razorpay API for payments
- ReportLab for PDF generation

### Frontend
- Bootstrap 4
- Django Crispy Forms
- Custom HTML/CSS templates
- Responsive design

## Security Features
- CSRF protection
- Secure password handling
- Email verification
- Secure payment processing
- Environment variable configuration

## Development Setup
1. Python environment with Django 3.2+
2. Required packages listed in requirements.txt
3. Configured email settings for notifications
4. Razorpay API keys for payment processing

## Project Configuration
- Timezone: Asia/Kolkata
- Language: English
- Debug mode: Enabled (for development)
- Media and static files properly configured
- Email backend configured for Gmail SMTP

## Important URLs
- Admin panel: /admin/
- User authentication: /accounts/
- Product catalog: /product/
- User dashboard: /user/
- Vendor panel: /vendor/
- Payment processing: /payment/
- Order management: /orders/

## Future Enhancements
- Social authentication
- Advanced search functionality
- Review and rating system
- Analytics dashboard
- Mobile application integration 