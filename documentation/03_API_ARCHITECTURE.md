# REST API Architecture - Complete Guide

**Part 4 of Complete Documentation Series**

---

## 📋 Table of Contents

1. [REST API Fundamentals](#rest-api-fundamentals)
2. [Django REST Framework Explained](#django-rest-framework-explained)
3. [Serializers Deep Dive](#serializers-deep-dive)
4. [Views and ViewSets](#views-and-viewsets)
5. [Authentication & Permissions](#authentication--permissions)
6. [Pagination System](#pagination-system)
7. [Filtering & Search](#filtering--search)
8. [Error Handling](#error-handling)

---

## 1. REST API Fundamentals

### What is REST?

**REST** = Representational State Transfer

### Core Principles

1. **Stateless:** Each request independent
2. **Client-Server:** Separate frontend and backend
3. **Cacheable:** Responses can be cached
4. **Uniform Interface:** Consistent API design

### HTTP Methods

```
GET    - Retrieve resource(s)     [Safe, Idempotent]
POST   - Create new resource       [Not Safe, Not Idempotent]
PUT    - Update entire resource    [Not Safe, Idempotent]
PATCH  - Update partial resource   [Not Safe, Not Idempotent]
DELETE - Remove resource           [Not Safe, Idempotent]
```

**Idempotent:** Multiple identical requests = same result

### HTTP Status Codes

```
200 OK                  - Successful GET/PATCH/PUT
201 Created             - Successful POST (resource created)
204 No Content          - Successful DELETE
400 Bad Request         - Validation errors
401 Unauthorized        - Authentication required
403 Forbidden           - Authenticated but no permission
404 Not Found           - Resource doesn't exist
500 Internal Server Error - Server error
```

### API Design

**Our API follows RESTful conventions:**

```
GET    /api/products/           - List all products
GET    /api/products/helmet-1/  - Get single product
POST   /api/products/           - Create product
PATCH  /api/products/helmet-1/  - Update product
DELETE /api/products/helmet-1/  - Delete product
```

---

## 2. Django REST Framework Explained

### What is DRF?

Django REST Framework = Toolkit for building Web APIs in Django

### Why DRF?

**Without DRF:**
```python
# Manual JSON response
import json
from django.http import JsonResponse

def product_list(request):
    products = Product.objects.all()
    data = []
    for product in products:
        data.append({
            'id': product.id,
            'title': product.title,
            'price': str(product.price)
        })
    return JsonResponse(data, safe=False)
```

**With DRF:**
```python
# Automatic serialization
class ProductListView(APIView):
    def get(self, request):
        products = Product.objects.all()
        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data)
```

### DRF Components

```
Request → View → Serializer → Model → Database
                      ↓
Response ← JSON ← Serializer ← QuerySet
```

---

## 3. Serializers Deep Dive

### What are Serializers?

**Serializers** convert complex data types to Python native types (JSON-compatible)

### Basic Serializer

**File:** `apps/api/serializers/catalog.py`

```python
class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category model"""
    product_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'image', 'parent_id', 'product_count']
    
    def get_product_count(self, obj):
        """Get active product count for category"""
        return obj.products.filter(is_active=True).count()
```

### Line-by-Line Explanation

**1. Inherit from ModelSerializer:**
```python
class CategorySerializer(serializers.ModelSerializer):
```
- **ModelSerializer:** Auto-generates fields from model
- **Alternative:** `serializers.Serializer` (manual field definition)

**2. Custom Field:**
```python
product_count = serializers.SerializerMethodField()
```
- **SerializerMethodField:** Computed field (not in database)
- **Naming convention:** Must have `get_<field_name>` method
- **Read-only:** Cannot be set via API

**3. Meta Class:**
```python
class Meta:
    model = Category
    fields = ['id', 'name', 'slug', ...]
```
- **model:** Which Django model to serialize
- **fields:** Which fields to include in JSON
- **Alternative:** `fields = '__all__'` (all model fields)
- **Exclude:** `exclude = ['internal_field']`

**4. Custom Method:**
```python
def get_product_count(self, obj):
    return obj.products.filter(is_active=True).count()
```
- **obj:** Instance of Category model
- **Access relationships:** `obj.products`
- **Return:** Must be JSON-serializable

### Nested Serializers

**Example:** Product with Category and Brand

```python
class ProductListSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    brand = BrandSerializer(read_only=True)
    primary_image = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'title', 'slug', 'category', 'brand',
            'price', 'sale_price', 'primary_image'
        ]
    
    def get_primary_image(self, obj):
        request = self.context.get('request')
        image = obj.images.filter(position=0).first()
        if image and image.image:
            return request.build_absolute_uri(image.image.url)
        return None
```

**Result:**
```json
{
  "id": 1,
  "title": "Mountain Bike Helmet",
  "slug": "mountain-bike-helmet",
  "category": {
    "id": 1,
    "name": "Helmets",
    "slug": "helmets"
  },
  "brand": {
    "id": 2,
    "name": "Giro",
    "slug": "giro"
  },
  "price": "5000.00",
  "sale_price": "4000.00",
  "primary_image": "http://localhost:8000/media/products/2024/11/helmet.jpg"
}
```

### Context in Serializers

**Passing context:**
```python
serializer = ProductListSerializer(
    products,
    many=True,
    context={'request': request}
)
```

**Using context:**
```python
def get_primary_image(self, obj):
    request = self.context.get('request')  # Access request
    if request:
        return request.build_absolute_uri(image.url)  # Full URL
    return image.url  # Relative URL
```

**Why pass request?**
- Build absolute URLs: `http://localhost:8000/media/...`
- Access user: `request.user`
- Access query params: `request.query_params`

---

## 4. Views and ViewSets

### APIView - Class-Based Views

**File:** `apps/api/views/catalog.py`

```python
class ProductListView(APIView):
    """
    GET /api/products/
    List all products with filtering and pagination
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        # Get queryset
        queryset = Product.objects.filter(is_active=True)
        
        # Apply filters
        category_slug = request.query_params.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        # Apply pagination
        paginator = LaravelStylePagination()
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        
        # Serialize
        serializer = ProductListSerializer(
            paginated_queryset,
            many=True,
            context={'request': request}
        )
        
        # Return paginated response
        return paginator.get_paginated_response(serializer.data)
```

### Line-by-Line Explanation

**1. Class Definition:**
```python
class ProductListView(APIView):
```
- **APIView:** Base class for DRF views
- **Provides:** Request parsing, authentication, permissions

**2. Permissions:**
```python
permission_classes = [AllowAny]
```
- **AllowAny:** No authentication required
- **Alternative:** `IsAuthenticated`, `IsAdminUser`
- **Can override per-method**

**3. HTTP Method Handler:**
```python
def get(self, request):
```
- **Method name = HTTP method:** get, post, patch, delete
- **request:** DRF Request object (enhanced Django request)
- **Returns:** DRF Response object

**4. Query Parameters:**
```python
category_slug = request.query_params.get('category')
```
- **query_params:** Dictionary of URL parameters
- **Example:** `?category=helmets&brand=giro`
- **DRF:** Uses `query_params` instead of `GET`

**5. Filtering:**
```python
queryset = queryset.filter(category__slug=category_slug)
```
- **Django ORM:** Chained filters
- **Lazy evaluation:** No database query until needed
- **Double underscore:** Traverse relationships (`category__slug`)

**6. Pagination:**
```python
paginator = LaravelStylePagination()
paginated_queryset = paginator.paginate_queryset(queryset, request)
```
- **paginate_queryset:** Applies LIMIT/OFFSET to query
- **Returns:** Slice of queryset (e.g., items 1-20)

**7. Serialization:**
```python
serializer = ProductListSerializer(paginated_queryset, many=True)
```
- **many=True:** Serialize list of objects
- **many=False (default):** Single object

**8. Response:**
```python
return paginator.get_paginated_response(serializer.data)
```
- **Wraps data:** Adds pagination metadata
- **Returns:** DRF Response object

### Detail View Example

```python
class ProductDetailView(APIView):
    """
    GET /api/products/{slug}/
    Retrieve single product by slug
    """
    permission_classes = [AllowAny]
    
    def get(self, request, slug):
        try:
            product = Product.objects.get(slug=slug, is_active=True)
        except Product.DoesNotExist:
            return Response(
                {'detail': 'Product not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = ProductDetailSerializer(product, context={'request': request})
        return Response(serializer.data)
```

**Key Points:**
- **URL parameter:** `slug` passed from URL pattern
- **Error handling:** Catch DoesNotExist exception
- **404 response:** Explicit error message
- **No pagination:** Single object

---

## 5. Authentication & Permissions

### JWT Authentication

**How it works:**

```
1. User logs in → Server generates JWT token
2. Client stores token (localStorage/cookies)
3. Client sends token with each request:
   Header: Authorization: Bearer eyJ0eXAiOiJKV1QiLCJ...
4. Server validates token → Authenticates user
```

### Token Structure

```
eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoxLCJleHAiOjE2MzI0NTY3ODl9.Xz7v9QJKL3x...
│                                     │                                      │
│          Header (Base64)            │         Payload (Base64)            │  Signature
│  {"typ":"JWT","alg":"HS256"}        │  {"user_id":1,"exp":1632456789}    │  (HMAC-SHA256)
```

**Payload includes:**
- `user_id` - Who is authenticated
- `exp` - Expiration timestamp
- `iat` - Issued at timestamp

### Login View

**File:** `apps/api/views/auth.py`

```python
class LoginView(APIView):
    """
    POST /api/auth/login/
    Authenticate user and return JWT token
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Get validated data
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        
        # Authenticate
        user = authenticate(email=email, password=password)
        
        if user is None:
            return Response(
                {'detail': 'Invalid email or password'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Generate token
        from api.serializers import generate_jwt_token
        token = generate_jwt_token(user)
        
        # Return user data + token
        return Response({
            'user': UserSerializer(user).data,
            'token': token
        })
```

### JWT Token Generation

```python
def generate_jwt_token(user):
    """Generate JWT access token for user"""
    from rest_framework_simplejwt.tokens import AccessToken
    
    token = AccessToken.for_user(user)
    return str(token)
```

**Under the hood:**
1. Creates payload with user_id and expiration
2. Signs with SECRET_KEY from settings
3. Returns encoded token string

### Protected Endpoints

```python
class ProfileView(APIView):
    """
    GET /api/auth/profile/
    Get current user's profile (authentication required)
    """
    permission_classes = [IsAuthenticated]  # ← Requires authentication
    
    def get(self, request):
        serializer = UserSerializer(request.user)  # ← request.user is authenticated user
        return Response(serializer.data)
```

**How authentication works:**

1. **Client sends request:**
   ```
   GET /api/auth/profile/
   Authorization: Bearer eyJ0eXAiOiJKV1QiLCJ...
   ```

2. **DRF Authentication middleware:**
   ```python
   # From settings.py
   'DEFAULT_AUTHENTICATION_CLASSES': [
       'rest_framework_simplejwt.authentication.JWTAuthentication',
   ]
   ```

3. **JWTAuthentication validates token:**
   - Decode JWT
   - Verify signature
   - Check expiration
   - Load user from database

4. **Set request.user:**
   ```python
   request.user = User.objects.get(id=token_payload['user_id'])
   ```

5. **Check permissions:**
   ```python
   if not request.user.is_authenticated:
       return 401 Unauthorized
   ```

---

## 6. Pagination System

### Laravel-Style Pagination

**File:** `apps/api/pagination.py`

```python
class LaravelStylePagination(PageNumberPagination):
    """
    Mimics Laravel's pagination format
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
    
    def get_paginated_response(self, data):
        return Response({
            'data': data,
            'meta': {
                'current_page': self.page.number,
                'from': self.page.start_index(),
                'last_page': self.page.paginator.num_pages,
                'per_page': self.page.paginator.per_page,
                'to': self.page.end_index(),
                'total': self.page.paginator.count,
                'links': self.get_links(),
                'path': self.request.build_absolute_uri().split('?')[0],
            }
        })
    
    def get_links(self):
        """Generate pagination links"""
        links = []
        
        # Previous link
        links.append({
            'url': self.get_previous_link(),
            'label': '&laquo; Previous',
            'page': self.page.number - 1 if self.page.has_previous() else None,
            'active': False
        })
        
        # Page numbers
        for num in self.page.paginator.page_range:
            links.append({
                'url': self.get_page_link(num),
                'label': str(num),
                'page': num,
                'active': num == self.page.number
            })
        
        # Next link
        links.append({
            'url': self.get_next_link(),
            'label': 'Next &raquo;',
            'page': self.page.number + 1 if self.page.has_next() else None,
            'active': False
        })
        
        return links
```

### Response Format

```json
{
  "data": [
    {
      "id": 1,
      "title": "Product 1",
      ...
    },
    ...
  ],
  "meta": {
    "current_page": 1,
    "from": 1,
    "last_page": 5,
    "per_page": 20,
    "to": 20,
    "total": 95,
    "path": "http://localhost:8000/api/products/",
    "links": [
      {
        "url": null,
        "label": "« Previous",
        "page": null,
        "active": false
      },
      {
        "url": "http://localhost:8000/api/products/?page=1",
        "label": "1",
        "page": 1,
        "active": true
      },
      {
        "url": "http://localhost:8000/api/products/?page=2",
        "label": "2",
        "page": 2,
        "active": false
      },
      {
        "url": "http://localhost:8000/api/products/?page=2",
        "label": "Next »",
        "page": 2,
        "active": false
      }
    ]
  }
}
```

---

## 7. Filtering & Search

### Django Filter Backend

**File:** `apps/api/views/catalog.py`

```python
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

class ProductListView(APIView):
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category__slug', 'brand__slug', 'is_active']
    search_fields = ['title', 'description']
    ordering_fields = ['price', 'created_at', 'title']
```

### Example Queries

```bash
# Filter by category
GET /api/products/?category=helmets

# Filter by brand
GET /api/products/?brand=giro

# Search in title/description
GET /api/products/?search=mountain

# Sort by price (ascending)
GET /api/products/?ordering=price

# Sort by price (descending)
GET /api/products/?ordering=-price

# Combine filters
GET /api/products/?category=helmets&brand=giro&ordering=-price&search=road
```

### Custom Filtering

```python
def get_queryset(self):
    queryset = Product.objects.filter(is_active=True)
    
    # Custom price range filter
    min_price = self.request.query_params.get('min_price')
    max_price = self.request.query_params.get('max_price')
    
    if min_price:
        queryset = queryset.filter(price__gte=min_price)
    if max_price:
        queryset = queryset.filter(price__lte=max_price)
    
    # Custom sale filter
    on_sale = self.request.query_params.get('on_sale')
    if on_sale == 'true':
        queryset = queryset.filter(sale_price__isnull=False)
    
    return queryset
```

---

## 8. Error Handling

### Validation Errors

```python
# Serializer validation
class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(min_length=8)
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already registered")
        return value
```

**Response (400 Bad Request):**
```json
{
  "email": ["Email already registered"]
}
```

### Custom Error Responses

```python
try:
    product = Product.objects.get(slug=slug)
except Product.DoesNotExist:
    return Response(
        {'detail': 'Product not found'},
        status=status.HTTP_404_NOT_FOUND
    )
```

### Success Response Wrapper

**File:** `apps/api/utils.py`

```python
def success_response(data=None, message="Success", status_code=200):
    """
    Standardize success responses
    """
    response = {}
    if message:
        response['message'] = message
    if data is not None:
        response['data'] = data
    
    return Response(response, status=status_code)
```

**Usage:**
```python
return success_response(
    data=serializer.data,
    message="Product retrieved successfully"
)
```

---

**Continue to `04_AUTHENTICATION_SYSTEM.md` for detailed authentication implementation.**
