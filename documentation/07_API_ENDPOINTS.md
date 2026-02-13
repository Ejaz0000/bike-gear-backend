# 07 - Complete API Endpoints Reference

**Last Updated:** November 23, 2025

This is a complete reference guide for all REST API endpoints in the BikeShop e-commerce platform.

---

## 📋 Table of Contents

1. [API Overview](#api-overview)
2. [Authentication](#authentication)
3. [Authentication Endpoints](#authentication-endpoints)
4. [User Profile Endpoints](#user-profile-endpoints)
5. [Address Management](#address-management)
6. [Catalog Endpoints](#catalog-endpoints)
7. [Cart Endpoints](#cart-endpoints)
8. [Order Endpoints](#order-endpoints)
9. [Homepage Endpoint](#homepage-endpoint)
10. [Error Responses](#error-responses)
11. [Status Codes](#status-codes)

---

## API Overview

### Base URL

```
Development: http://localhost:8000/api/
Production: https://yourdomain.com/api/
```

### Response Format

All API responses follow a standardized format:

**Success Response:**
```json
{
  "success": true,
  "data": { ... },
  "message": "Optional success message"
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "Error message",
  "errors": {
    "field_name": ["Error detail"]
  }
}
```

### Authentication Header

For protected endpoints, include JWT token:

```http
Authorization: Bearer <your_jwt_token>
```

---

## Authentication

### How JWT Works

```
1. User registers/logs in
   ↓
2. Server returns access token + refresh token
   ↓
3. Client includes access token in requests
   ↓
4. Server validates token
   ↓
5. Access granted/denied
```

### Token Lifetime

- **Access Token:** 60 minutes
- **Refresh Token:** 1 day

---

## Authentication Endpoints

### 1. Register New User

**Endpoint:** `POST /api/auth/register/`

**Authentication:** Not required

**Description:** Create a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "password2": "SecurePass123!",
  "name": "John Doe",
  "phone": "1234567890"
}
```

**Field Validations:**
- `email`: Valid email format, unique
- `password`: Min 8 characters
- `password2`: Must match password
- `name`: Required, max 100 characters
- `phone`: Optional, max 15 characters

**Success Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": 1,
      "email": "user@example.com",
      "name": "John Doe",
      "phone": "1234567890"
    },
    "tokens": {
      "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
      "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
    }
  },
  "message": "Registration successful"
}
```

**Error Response (400 Bad Request):**
```json
{
  "success": false,
  "error": "Validation failed",
  "errors": {
    "email": ["User with this email already exists."],
    "password2": ["Passwords do not match."]
  }
}
```

**Code Example:**
```javascript
// JavaScript/Fetch
const response = await fetch('http://localhost:8000/api/auth/register/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'SecurePass123!',
    password2: 'SecurePass123!',
    name: 'John Doe',
    phone: '1234567890'
  })
});

const data = await response.json();
console.log(data);

// Store tokens
localStorage.setItem('access_token', data.data.tokens.access);
localStorage.setItem('refresh_token', data.data.tokens.refresh);
```

---

### 2. Login

**Endpoint:** `POST /api/auth/login/`

**Authentication:** Not required

**Description:** Authenticate user and receive JWT tokens.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": 1,
      "email": "user@example.com",
      "name": "John Doe",
      "phone": "1234567890",
      "is_staff": false
    },
    "tokens": {
      "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
      "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
    }
  },
  "message": "Login successful"
}
```

**Error Response (401 Unauthorized):**
```json
{
  "success": false,
  "error": "Invalid email or password"
}
```

**Code Example:**
```python
# Python/Requests
import requests

response = requests.post('http://localhost:8000/api/auth/login/', json={
    'email': 'user@example.com',
    'password': 'SecurePass123!'
})

data = response.json()
access_token = data['data']['tokens']['access']

# Use token in subsequent requests
headers = {'Authorization': f'Bearer {access_token}'}
```

---

### 3. Forgot Password

**Endpoint:** `POST /api/auth/forgot-password/`

**Authentication:** Not required

**Description:** Request password reset token via email.

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Password reset token sent to your email"
}
```

**Note:** In development, token is printed to console. In production, sent via email.

---

### 4. Verify Reset Token

**Endpoint:** `POST /api/auth/verify-reset-token/`

**Authentication:** Not required

**Description:** Verify if reset token is valid before allowing password reset.

**Request Body:**
```json
{
  "token": "123456"
}
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Token is valid"
}
```

**Error Response (400 Bad Request):**
```json
{
  "success": false,
  "error": "Invalid or expired token"
}
```

---

### 5. Reset Password

**Endpoint:** `POST /api/auth/reset-password/`

**Authentication:** Not required

**Description:** Reset password using valid token.

**Request Body:**
```json
{
  "token": "123456",
  "new_password": "NewSecurePass123!",
  "confirm_password": "NewSecurePass123!"
}
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Password reset successful"
}
```

**Error Response (400 Bad Request):**
```json
{
  "success": false,
  "error": "Passwords do not match"
}
```

---

## User Profile Endpoints

### 6. Get User Profile

**Endpoint:** `GET /api/auth/profile/`

**Authentication:** Required (JWT)

**Description:** Get current user's profile information.

**Request Headers:**
```http
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "email": "user@example.com",
    "name": "John Doe",
    "phone": "1234567890",
    "is_staff": false,
    "date_joined": "2025-11-23T10:30:00Z"
  }
}
```

**Error Response (401 Unauthorized):**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

---

### 7. Update User Profile

**Endpoint:** `PUT /api/auth/profile/`

**Authentication:** Required (JWT)

**Description:** Update current user's profile.

**Request Body:**
```json
{
  "name": "John Smith",
  "phone": "9876543210"
}
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "email": "user@example.com",
    "name": "John Smith",
    "phone": "9876543210",
    "is_staff": false
  },
  "message": "Profile updated successfully"
}
```

**Note:** Email cannot be changed via this endpoint for security reasons.

---

### 8. Change Password

**Endpoint:** `POST /api/auth/change-password/`

**Authentication:** Required (JWT)

**Description:** Change password for authenticated user.

**Request Body:**
```json
{
  "old_password": "OldPass123!",
  "new_password": "NewSecurePass123!",
  "confirm_password": "NewSecurePass123!"
}
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Password changed successfully"
}
```

**Error Response (400 Bad Request):**
```json
{
  "success": false,
  "error": "Validation failed",
  "errors": {
    "old_password": ["Current password is incorrect"],
    "confirm_password": ["Passwords do not match"]
  }
}
```

---

## Address Management

### 9. List User Addresses

**Endpoint:** `GET /api/auth/addresses/`

**Authentication:** Required (JWT)

**Description:** Get all addresses for current user.

**Success Response (200 OK):**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "address_type": "home",
      "street_address": "123 Main St",
      "apartment": "Apt 4B",
      "city": "New York",
      "state": "NY",
      "postal_code": "10001",
      "country": "USA",
      "phone": "1234567890",
      "is_default": true,
      "created_at": "2025-11-23T10:30:00Z"
    },
    {
      "id": 2,
      "address_type": "work",
      "street_address": "456 Office Ave",
      "apartment": "Suite 200",
      "city": "New York",
      "state": "NY",
      "postal_code": "10002",
      "country": "USA",
      "phone": "9876543210",
      "is_default": false,
      "created_at": "2025-11-24T14:20:00Z"
    }
  ]
}
```

---

### 10. Create Address

**Endpoint:** `POST /api/auth/addresses/`

**Authentication:** Required (JWT)

**Description:** Add a new address for current user.

**Request Body:**
```json
{
  "address_type": "home",
  "street_address": "123 Main St",
  "apartment": "Apt 4B",
  "city": "New York",
  "state": "NY",
  "postal_code": "10001",
  "country": "USA",
  "phone": "1234567890",
  "is_default": true
}
```

**Field Options:**
- `address_type`: "home", "work", or "other"
- `is_default`: If true, sets this as default and removes default from other addresses

**Success Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "id": 3,
    "address_type": "home",
    "street_address": "123 Main St",
    "apartment": "Apt 4B",
    "city": "New York",
    "state": "NY",
    "postal_code": "10001",
    "country": "USA",
    "phone": "1234567890",
    "is_default": true,
    "created_at": "2025-11-25T09:15:00Z"
  },
  "message": "Address created successfully"
}
```

---

### 11. Get Address Detail

**Endpoint:** `GET /api/auth/addresses/{id}/`

**Authentication:** Required (JWT)

**Description:** Get specific address details.

**Success Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "address_type": "home",
    "street_address": "123 Main St",
    "apartment": "Apt 4B",
    "city": "New York",
    "state": "NY",
    "postal_code": "10001",
    "country": "USA",
    "phone": "1234567890",
    "is_default": true
  }
}
```

---

### 12. Update Address

**Endpoint:** `PUT /api/auth/addresses/{id}/`

**Authentication:** Required (JWT)

**Description:** Update an existing address.

**Request Body:**
```json
{
  "address_type": "work",
  "street_address": "789 New Address",
  "city": "Boston",
  "state": "MA",
  "postal_code": "02101",
  "is_default": false
}
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "address_type": "work",
    "street_address": "789 New Address",
    "city": "Boston",
    "state": "MA",
    "postal_code": "02101",
    "is_default": false
  },
  "message": "Address updated successfully"
}
```

---

### 13. Delete Address

**Endpoint:** `DELETE /api/auth/addresses/{id}/`

**Authentication:** Required (JWT)

**Description:** Delete an address.

**Success Response (204 No Content):**
```json
{
  "success": true,
  "message": "Address deleted successfully"
}
```

---

## Catalog Endpoints

### 14. List Products

**Endpoint:** `GET /api/products/`

**Authentication:** Not required

**Description:** Get paginated list of products with filtering and searching.

**Query Parameters:**

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `search` | string | Search in title/description | `?search=bike` |
| `category` | string | Filter by category slug(s) | `?category=mountain-bikes` |
| `brand` | string | Filter by brand slug(s) | `?brand=trek,specialized` |
| `min_price` | decimal | Minimum price | `?min_price=500` |
| `max_price` | decimal | Maximum price | `?max_price=1500` |
| `on_sale` | boolean | Show only sale items | `?on_sale=true` |
| `ordering` | string | Sort order | `?ordering=-price` |
| `page` | integer | Page number | `?page=2` |
| `page_size` | integer | Items per page | `?page_size=20` |

**Ordering Options:**
- `price` - Low to high
- `-price` - High to low
- `created_at` - Oldest first
- `-created_at` - Newest first (default)
- `title` - A to Z
- `-title` - Z to A

**Example Request:**
```
GET /api/products/?category=mountain-bikes&brand=trek&min_price=500&max_price=1500&ordering=price
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "count": 45,
    "next": "http://localhost:8000/api/products/?page=2",
    "previous": null,
    "results": [
      {
        "id": 1,
        "title": "Trek Marlin 7 Mountain Bike",
        "slug": "trek-marlin-7-mountain-bike",
        "category": {
          "id": 2,
          "name": "Mountain Bikes",
          "slug": "mountain-bikes",
          "product_count": 15
        },
        "brand": {
          "id": 1,
          "name": "Trek",
          "slug": "trek",
          "product_count": 23
        },
        "price": "799.99",
        "sale_price": "699.99",
        "min_price": "699.99",
        "max_price": "799.99",
        "is_on_sale": true,
        "discount_percentage": 13,
        "stock": 15,
        "primary_image": "http://localhost:8000/media/products/2025/11/trek-marlin.jpg",
        "variant_count": 3
      }
    ]
  }
}
```

**Code Example:**
```javascript
// Fetch products with filters
const fetchProducts = async () => {
  const params = new URLSearchParams({
    category: 'mountain-bikes',
    brand: 'trek',
    min_price: '500',
    max_price: '1500',
    ordering: 'price',
    page: '1'
  });
  
  const response = await fetch(`http://localhost:8000/api/products/?${params}`);
  const data = await response.json();
  
  console.log(`Total products: ${data.data.count}`);
  console.log(`Products on this page: ${data.data.results.length}`);
  
  return data.data.results;
};
```

---

### 15. Get Product Detail

**Endpoint:** `GET /api/products/{slug}/`

**Authentication:** Not required

**Description:** Get detailed product information including variants, images, and attributes.

**Example Request:**
```
GET /api/products/trek-marlin-7-mountain-bike/
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "title": "Trek Marlin 7 Mountain Bike",
    "slug": "trek-marlin-7-mountain-bike",
    "description": "The Trek Marlin 7 is the perfect gateway to trail riding. It's ideal for new riders who want a mountain bike with knobby tires...",
    "category": {
      "id": 2,
      "name": "Mountain Bikes",
      "slug": "mountain-bikes",
      "description": "All-terrain bicycles for trail riding",
      "image": "http://localhost:8000/media/categories/mountain.jpg",
      "product_count": 15
    },
    "brand": {
      "id": 1,
      "name": "Trek",
      "slug": "trek",
      "description": "American bicycle manufacturer",
      "logo": "http://localhost:8000/media/brands/trek-logo.jpg",
      "website": "https://www.trekbikes.com",
      "product_count": 23
    },
    "price": "799.99",
    "sale_price": "699.99",
    "stock": 15,
    "weight": "13.50",
    "length": "180.00",
    "width": "60.00",
    "height": "110.00",
    "meta_title": "Trek Marlin 7 Mountain Bike - Buy Online",
    "meta_description": "Shop the Trek Marlin 7 mountain bike...",
    "images": [
      {
        "id": 1,
        "image": "http://localhost:8000/media/products/2025/11/trek-marlin-1.jpg",
        "alt_text": "Trek Marlin 7 - Front View",
        "position": 0
      },
      {
        "id": 2,
        "image": "http://localhost:8000/media/products/2025/11/trek-marlin-2.jpg",
        "alt_text": "Trek Marlin 7 - Side View",
        "position": 1
      }
    ],
    "variants": [
      {
        "id": 1,
        "sku": "TREK-M7-SM-RED",
        "price": "699.99",
        "sale_price": null,
        "stock": 5,
        "is_on_sale": false,
        "discount_percentage": null,
        "is_in_stock": true,
        "attributes": [
          {
            "type": "Size",
            "value": "Small"
          },
          {
            "type": "Color",
            "value": "Red"
          }
        ]
      },
      {
        "id": 2,
        "sku": "TREK-M7-MD-BLUE",
        "price": "699.99",
        "sale_price": "649.99",
        "stock": 10,
        "is_on_sale": true,
        "discount_percentage": 7,
        "is_in_stock": true,
        "attributes": [
          {
            "type": "Size",
            "value": "Medium"
          },
          {
            "type": "Color",
            "value": "Blue"
          }
        ]
      }
    ],
    "created_at": "2025-11-20T10:30:00Z",
    "updated_at": "2025-11-23T15:45:00Z"
  }
}
```

**Error Response (404 Not Found):**
```json
{
  "detail": "Not found."
}
```

---

### 16. List Categories

**Endpoint:** `GET /api/categories/`

**Authentication:** Not required

**Description:** Get all active categories.

**Success Response (200 OK):**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "Bikes",
      "slug": "bikes",
      "description": "All types of bicycles",
      "image": "http://localhost:8000/media/categories/bikes.jpg",
      "parent_id": null,
      "product_count": 45
    },
    {
      "id": 2,
      "name": "Mountain Bikes",
      "slug": "mountain-bikes",
      "description": "All-terrain bicycles",
      "image": "http://localhost:8000/media/categories/mountain.jpg",
      "parent_id": 1,
      "product_count": 15
    }
  ]
}
```

---

### 17. Get Category Detail

**Endpoint:** `GET /api/categories/{slug}/`

**Authentication:** Not required

**Description:** Get category with its products.

**Example Request:**
```
GET /api/categories/mountain-bikes/
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": 2,
    "name": "Mountain Bikes",
    "slug": "mountain-bikes",
    "description": "All-terrain bicycles for trail riding",
    "image": "http://localhost:8000/media/categories/mountain.jpg",
    "parent_id": 1,
    "product_count": 15,
    "products": [
      {
        "id": 1,
        "title": "Trek Marlin 7 Mountain Bike",
        "slug": "trek-marlin-7-mountain-bike",
        "price": "799.99",
        "primary_image": "http://localhost:8000/media/products/trek-marlin.jpg"
      }
    ]
  }
}
```

---

### 18. List Brands

**Endpoint:** `GET /api/brands/`

**Authentication:** Not required

**Description:** Get all active brands.

**Success Response (200 OK):**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "Trek",
      "slug": "trek",
      "description": "American bicycle manufacturer",
      "logo": "http://localhost:8000/media/brands/trek-logo.jpg",
      "website": "https://www.trekbikes.com",
      "product_count": 23
    },
    {
      "id": 2,
      "name": "Specialized",
      "slug": "specialized",
      "description": "Premium bicycle brand",
      "logo": "http://localhost:8000/media/brands/specialized-logo.jpg",
      "website": "https://www.specialized.com",
      "product_count": 18
    }
  ]
}
```

---

### 19. Get Brand Detail

**Endpoint:** `GET /api/brands/{slug}/`

**Authentication:** Not required

**Description:** Get brand with its products.

**Example Request:**
```
GET /api/brands/trek/
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "Trek",
    "slug": "trek",
    "description": "American bicycle manufacturer founded in 1976...",
    "logo": "http://localhost:8000/media/brands/trek-logo.jpg",
    "website": "https://www.trekbikes.com",
    "product_count": 23,
    "products": [
      {
        "id": 1,
        "title": "Trek Marlin 7 Mountain Bike",
        "slug": "trek-marlin-7-mountain-bike",
        "price": "799.99",
        "primary_image": "http://localhost:8000/media/products/trek-marlin.jpg"
      }
    ]
  }
}
```

---

## Cart Endpoints

### 20. Get Cart

**Endpoint:** `GET /api/cart/`

**Authentication:** Optional (works for both guest and authenticated users)

**Description:** Get current user's cart (session-based for guests, database for authenticated).

**Success Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "items": [
      {
        "id": 1,
        "product": {
          "id": 1,
          "title": "Trek Marlin 7 Mountain Bike",
          "slug": "trek-marlin-7-mountain-bike"
        },
        "variant": {
          "id": 1,
          "sku": "TREK-M7-SM-RED",
          "price": "699.99",
          "sale_price": null,
          "stock": 5,
          "attributes": [
            {"type": "Size", "value": "Small"},
            {"type": "Color", "value": "Red"}
          ]
        },
        "quantity": 2,
        "unit_price": "699.99",
        "total_price": "1399.98"
      }
    ],
    "total_items": 2,
    "subtotal": "1399.98",
    "created_at": "2025-11-23T10:30:00Z",
    "updated_at": "2025-11-23T11:45:00Z"
  }
}
```

**Empty Cart Response:**
```json
{
  "success": true,
  "data": {
    "items": [],
    "total_items": 0,
    "subtotal": "0.00"
  }
}
```

---

### 21. Add to Cart

**Endpoint:** `POST /api/cart/items/`

**Authentication:** Optional

**Description:** Add a product variant to cart.

**Request Body:**
```json
{
  "variant_id": 1,
  "quantity": 2
}
```

**Success Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "product": {
      "id": 1,
      "title": "Trek Marlin 7 Mountain Bike",
      "slug": "trek-marlin-7-mountain-bike"
    },
    "variant": {
      "id": 1,
      "sku": "TREK-M7-SM-RED",
      "price": "699.99",
      "stock": 5
    },
    "quantity": 2,
    "unit_price": "699.99",
    "total_price": "1399.98"
  },
  "message": "Item added to cart"
}
```

**Error Response (400 Bad Request):**
```json
{
  "success": false,
  "error": "Insufficient stock. Only 1 unit available."
}
```

---

### 22. Update Cart Item

**Endpoint:** `PUT /api/cart/items/{id}/`

**Authentication:** Optional

**Description:** Update quantity of cart item.

**Request Body:**
```json
{
  "quantity": 3
}
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "quantity": 3,
    "unit_price": "699.99",
    "total_price": "2099.97"
  },
  "message": "Cart item updated"
}
```

---

### 23. Remove Cart Item

**Endpoint:** `DELETE /api/cart/items/{id}/`

**Authentication:** Optional

**Description:** Remove item from cart.

**Success Response (204 No Content):**
```json
{
  "success": true,
  "message": "Item removed from cart"
}
```

---

### 24. Clear Cart

**Endpoint:** `POST /api/cart/clear/`

**Authentication:** Optional

**Description:** Remove all items from cart.

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Cart cleared successfully"
}
```

---

## Order Endpoints

### 25. Create Order

**Endpoint:** `POST /api/orders/create/`

**Authentication:** Required (JWT)

**Description:** Create order from current cart.

**Request Body:**
```json
{
  "shipping_address_id": 1,
  "billing_address_id": 1,
  "payment_method": "credit_card",
  "notes": "Please deliver after 5 PM"
}
```

**Success Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "order_number": "ORD-20251123-001",
    "status": "pending",
    "items": [
      {
        "product_title": "Trek Marlin 7 Mountain Bike",
        "variant_sku": "TREK-M7-SM-RED",
        "quantity": 2,
        "unit_price": "699.99",
        "total_price": "1399.98"
      }
    ],
    "subtotal": "1399.98",
    "shipping_cost": "0.00",
    "tax": "0.00",
    "total": "1399.98",
    "shipping_address": {
      "street_address": "123 Main St",
      "city": "New York",
      "state": "NY",
      "postal_code": "10001"
    },
    "created_at": "2025-11-23T12:00:00Z"
  },
  "message": "Order created successfully"
}
```

**Error Response (400 Bad Request):**
```json
{
  "success": false,
  "error": "Cart is empty"
}
```

---

### 26. List Orders

**Endpoint:** `GET /api/orders/`

**Authentication:** Required (JWT)

**Description:** Get all orders for current user.

**Success Response (200 OK):**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "order_number": "ORD-20251123-001",
      "status": "pending",
      "total": "1399.98",
      "created_at": "2025-11-23T12:00:00Z"
    },
    {
      "id": 2,
      "order_number": "ORD-20251120-002",
      "status": "delivered",
      "total": "549.99",
      "created_at": "2025-11-20T09:30:00Z"
    }
  ]
}
```

---

### 27. Get Order Detail

**Endpoint:** `GET /api/orders/{order_number}/`

**Authentication:** Required (JWT)

**Description:** Get detailed order information.

**Example Request:**
```
GET /api/orders/ORD-20251123-001/
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "order_number": "ORD-20251123-001",
    "status": "pending",
    "items": [
      {
        "id": 1,
        "product_title": "Trek Marlin 7 Mountain Bike",
        "variant_sku": "TREK-M7-SM-RED",
        "quantity": 2,
        "unit_price": "699.99",
        "total_price": "1399.98"
      }
    ],
    "subtotal": "1399.98",
    "shipping_cost": "0.00",
    "tax": "0.00",
    "total": "1399.98",
    "shipping_address": {
      "street_address": "123 Main St",
      "apartment": "Apt 4B",
      "city": "New York",
      "state": "NY",
      "postal_code": "10001",
      "country": "USA"
    },
    "billing_address": {
      "street_address": "123 Main St",
      "apartment": "Apt 4B",
      "city": "New York",
      "state": "NY",
      "postal_code": "10001",
      "country": "USA"
    },
    "payment_method": "credit_card",
    "notes": "Please deliver after 5 PM",
    "created_at": "2025-11-23T12:00:00Z",
    "updated_at": "2025-11-23T12:00:00Z"
  }
}
```

---

### 28. Cancel Order

**Endpoint:** `POST /api/orders/{order_number}/cancel/`

**Authentication:** Required (JWT)

**Description:** Cancel a pending order.

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Order cancelled successfully"
}
```

**Error Response (400 Bad Request):**
```json
{
  "success": false,
  "error": "Only pending orders can be cancelled"
}
```

---

## Homepage Endpoint

### 29. Get Homepage Data

**Endpoint:** `GET /api/homepage/`

**Authentication:** Not required

**Description:** Get homepage content (banners, featured sections, products).

**Success Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "banners": [
      {
        "id": 1,
        "title": "Summer Sale",
        "description": "Up to 50% off on all bikes",
        "image": "http://localhost:8000/media/banners/summer-sale.jpg",
        "button_text": "Shop Now",
        "button_url": "/products/?on_sale=true",
        "position": 0
      }
    ],
    "featured_sections": [
      {
        "id": 1,
        "title": "Best Sellers",
        "description": "Top products this month",
        "products": [
          {
            "id": 1,
            "title": "Trek Marlin 7 Mountain Bike",
            "slug": "trek-marlin-7-mountain-bike",
            "price": "799.99",
            "sale_price": "699.99",
            "primary_image": "http://localhost:8000/media/products/trek-marlin.jpg"
          }
        ]
      }
    ]
  }
}
```

---

## Error Responses

### Common Error Types

**1. Validation Error (400 Bad Request):**
```json
{
  "success": false,
  "error": "Validation failed",
  "errors": {
    "field_name": ["Error message"]
  }
}
```

**2. Unauthorized (401):**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

**3. Forbidden (403):**
```json
{
  "detail": "You do not have permission to perform this action."
}
```

**4. Not Found (404):**
```json
{
  "detail": "Not found."
}
```

**5. Server Error (500):**
```json
{
  "success": false,
  "error": "Internal server error"
}
```

---

## Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created successfully |
| 204 | No Content | Request successful, no response body |
| 400 | Bad Request | Invalid request data |
| 401 | Unauthorized | Authentication required |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 500 | Internal Server Error | Server error |

---

## Testing with cURL

### Register
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123!",
    "password2": "SecurePass123!",
    "name": "Test User"
  }'
```

### Login
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123!"
  }'
```

### Get Products
```bash
curl http://localhost:8000/api/products/
```

### Get Cart (with auth)
```bash
curl http://localhost:8000/api/cart/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

**Next:** [08_ADMIN_DASHBOARD.md](./08_ADMIN_DASHBOARD.md) - Admin Dashboard Documentation

**Previous:** [06_CATALOG_PRODUCTS.md](./06_CATALOG_PRODUCTS.md) - Catalog System Documentation
