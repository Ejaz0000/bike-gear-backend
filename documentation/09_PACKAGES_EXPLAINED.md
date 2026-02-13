# BikeShop E-Commerce - Complete Packages & Dependencies Explained

**Part 9 of Complete Documentation Series**

---

## 📋 All Packages Explained

This document explains every package in `Pipfile` and why it's used.

---

## Core Framework

### 1. Django (`django = "*"`)

**What it is:** High-level Python web framework

**Why we use it:**
- Batteries-included framework
- Built-in ORM (database abstraction)
- Admin interface out of the box
- Security features (CSRF, XSS, SQL injection protection)
- Authentication system
- Form handling
- Template engine

**What it does in our project:**
- Core framework for entire application
- Manages database models
- Handles HTTP requests/responses
- Provides admin panel at `/admin/`
- User authentication

**Without it:** Would need to build everything from scratch

**Configuration:** `bike_shop/settings.py`

---

## API Framework

### 2. Django REST Framework (`djangorestframework = "*"`)

**What it is:** Powerful toolkit for building Web APIs

**Why we use it:**
- Industry standard for Django APIs
- Browsable API interface
- Serialization (Python objects ↔ JSON)
- Authentication classes
- Permission system
- Pagination
- Filtering
- Throttling

**What it does in our project:**
- Powers all `/api/` endpoints
- Converts Django models to JSON
- Handles API authentication (JWT)
- Provides pagination for product lists
- Enables filtering and search

**Example:**
```python
# Without DRF - Manual work
def products(request):
    products = Product.objects.all()
    data = [{'id': p.id, 'name': p.name} for p in products]
    return JsonResponse(data, safe=False)

# With DRF - Automatic
class ProductListView(APIView):
    def get(self, request):
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)
```

**Configuration:** `settings.py` → `REST_FRAMEWORK`

---

## Authentication

### 3. Simple JWT (`djangorestframework-simplejwt = "*"`)

**What it is:** JSON Web Token authentication for DRF

**Why we use it:**
- Stateless authentication (no server-side sessions)
- Perfect for mobile apps and SPAs
- Industry standard (OAuth 2.0, OpenID Connect use JWT)
- Self-contained (token contains all info)
- Scalable (works with multiple servers)

**What it does in our project:**
- Generates JWT tokens on login
- Validates tokens on protected endpoints
- 7-day token validity
- No refresh tokens (simplified approach)

**How it works:**
```
1. User logs in → POST /api/auth/login/
2. Server validates credentials
3. Server generates JWT token
4. Client stores token
5. Client sends token with each request:
   Authorization: Bearer eyJ0eXAiOiJKV1QiLCJ...
6. Server validates token → authenticates user
```

**Token structure:**
```
Header.Payload.Signature
eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.  ← Algorithm
eyJ1c2VyX2lkIjoxLCJleHAiOjE2MzI0NTY3ODl9.  ← User data + expiration
Xz7v9QJKL3x...  ← Signature (prevents tampering)
```

**Configuration:** `settings.py` → `SIMPLE_JWT`

**Alternative:** Django's built-in sessions (stateful, requires cookies)

---

## CORS (Cross-Origin Resource Sharing)

### 4. Django CORS Headers (`django-cors-headers = "*"`)

**What it is:** Handles Cross-Origin Resource Sharing

**Why we use it:**
- Backend (localhost:8000) and frontend (localhost:3000) are different origins
- Browsers block cross-origin requests by default (security)
- This package tells browsers "allow requests from localhost:3000"

**What it does in our project:**
- Adds CORS headers to responses
- Allows React frontend to call API
- Allows mobile apps to call API

**The problem without it:**
```
Frontend (localhost:3000) → API (localhost:8000)
Browser: ❌ "Blocked by CORS policy"
```

**With django-cors-headers:**
```
Frontend (localhost:3000) → API (localhost:8000)
Response includes: Access-Control-Allow-Origin: http://localhost:3000
Browser: ✅ "Request allowed"
```

**Configuration:**
```python
# settings.py
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # React dev server
    "http://127.0.0.1:3000",
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # Must be first!
    # ...other middleware
]
```

**Production:** Set specific origins, not `CORS_ALLOW_ALL = True`

---

## Image Processing

### 5. Pillow (`pillow = "*"`)

**What it is:** Python Imaging Library (PIL fork)

**Why we use it:**
- Django's `ImageField` requires Pillow
- Validates uploaded images
- Can resize/crop images
- Generates thumbnails
- Supports many formats (JPEG, PNG, GIF, WebP)

**What it does in our project:**
- Validates product images
- Validates category images
- Validates brand logos
- Handles image uploads

**Example:**
```python
# Model with ImageField
class Product(models.Model):
    image = models.ImageField(upload_to='products/')
    # ↑ Requires Pillow to work
```

**Without it:** `ImageField` won't work, get error

**Common operations (not used yet, but available):**
```python
from PIL import Image

# Resize image
img = Image.open('photo.jpg')
img.thumbnail((300, 300))
img.save('thumbnail.jpg')

# Convert format
img.save('photo.png', 'PNG')

# Crop image
box = (100, 100, 400, 400)
region = img.crop(box)
```

---

## Filtering

### 6. Django Filter (`django-filter = "*"`)

**What it is:** Reusable Django app for filtering querysets

**Why we use it:**
- Easy filtering in APIs
- Supports complex filters
- Integrates with DRF
- URL-based filtering

**What it does in our project:**
- Filter products by category: `?category=helmets`
- Filter products by brand: `?brand=giro`
- Filter by price range: `?min_price=1000&max_price=5000`
- Filter by sale status: `?on_sale=true`

**Configuration:**
```python
# settings.py
REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
    ],
}

# views.py
class ProductListView(generics.ListAPIView):
    queryset = Product.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category__slug', 'brand__slug']
```

**Example requests:**
```bash
GET /api/products/
GET /api/products/?category=helmets
GET /api/products/?category=helmets&brand=giro
GET /api/products/?min_price=1000&max_price=5000
```

---

## Environment Variables

### 7. Python Dotenv (`python-dotenv = "*"`)

**What it is:** Loads environment variables from `.env` file

**Why we use it:**
- Keep secrets out of code
- Different settings per environment (dev/staging/prod)
- Security best practice

**What it does in our project:**
- Loads `.env` file on startup
- Makes variables available to settings.py

**Example `.env` file:**
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DB_NAME=bikeshop_db
DB_USER=root
DB_PASSWORD=secret
EMAIL_HOST_USER=smtp@gmail.com
EMAIL_HOST_PASSWORD=app-password
```

**Usage in settings.py:**
```python
import os
from dotenv import load_dotenv

load_dotenv()  # Load .env file

SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = os.getenv('DEBUG') == 'True'
```

**Security:** Never commit `.env` to git (add to `.gitignore`)

---

## Database Adapters

### 8. MySQL Client (`mysqlclient = "*"`)

**What it is:** Python interface to MySQL database

**Why we use it:**
- Django needs database adapter
- MySQL is production database choice
- Better performance than SQLite

**What it does in our project:**
- Currently not used (using SQLite for development)
- Ready for production MySQL deployment

**Configuration for MySQL:**
```python
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'bikeshop_db',
        'USER': 'root',
        'PASSWORD': 'secret',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

**Alternative:** PostgreSQL with `psycopg2`

### 9. PostgreSQL Adapter (`psycopg2-binary = "*"`)

**What it is:** PostgreSQL adapter for Python

**Why included:**
- Alternative to MySQL
- PostgreSQL is popular for Django
- Better for complex queries
- Better JSON support

**Not currently used:** Available if needed

**Configuration for PostgreSQL:**
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'bikeshop_db',
        'USER': 'postgres',
        'PASSWORD': 'secret',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

---

## Dependency Management

### Pipenv

**What it is:** Python dependency management tool

**Why we use it:**
- Combines pip and virtualenv
- Creates virtual environment automatically
- Manages dependencies
- Locks versions for reproducibility

**Files:**
- `Pipfile` - Lists dependencies (like package.json)
- `Pipfile.lock` - Locks exact versions (like package-lock.json)

**Commands:**
```bash
pipenv install              # Install all dependencies
pipenv install django       # Add new dependency
pipenv shell                # Activate virtual environment
pipenv lock                 # Lock dependency versions
```

**Benefits over pip + requirements.txt:**
- Automatic virtual environment
- Separates dev dependencies
- Deterministic builds (lock file)
- Better dependency resolution

---

## Package Versions

**Current setup:** `package = "*"` (any version)

**Recommendation for production:**
```toml
[packages]
django = "~=5.2.7"                    # Compatible with 5.2.x
djangorestframework = "~=3.14.0"
djangorestframework-simplejwt = "~=5.3.0"
django-cors-headers = "~=4.3.0"
pillow = "~=10.1.0"
python-dotenv = "~=1.0.0"
django-filter = "~=23.5"
```

**Why pin versions?**
- Prevent breaking changes
- Reproducible deployments
- Easier debugging

---

## Summary Table

| Package | Purpose | Can Remove? | Alternative |
|---------|---------|-------------|-------------|
| django | Core framework | ❌ No | Flask, FastAPI |
| djangorestframework | API framework | ❌ No | Build manually |
| simplejwt | JWT auth | ⚠️ Yes | Django sessions |
| cors-headers | CORS support | ⚠️ Yes (backend-only) | Nginx config |
| pillow | Image handling | ⚠️ Yes (no images) | - |
| django-filter | API filtering | ✅ Yes | Manual filters |
| python-dotenv | Environment vars | ✅ Yes | OS env vars |
| mysqlclient | MySQL adapter | ✅ Yes | Use PostgreSQL |
| psycopg2-binary | PostgreSQL adapter | ✅ Yes | Use MySQL |

---

## Future Packages to Consider

### Payment Processing
```bash
pipenv install stripe         # Stripe payments
pipenv install paypalrestsdk  # PayPal
```

### Caching
```bash
pipenv install redis          # Redis caching
pipenv install django-redis   # Django Redis integration
```

### Email
```bash
pipenv install sendgrid       # SendGrid email service
```

### Celery (Background Tasks)
```bash
pipenv install celery         # Async task queue
pipenv install redis          # Celery broker
```

### Testing
```bash
pipenv install --dev pytest           # Testing framework
pipenv install --dev pytest-django    # Django testing
pipenv install --dev factory-boy      # Test data factories
```

### Code Quality
```bash
pipenv install --dev black            # Code formatter
pipenv install --dev flake8           # Linter
pipenv install --dev pylint           # Another linter
```

### Documentation
```bash
pipenv install drf-spectacular        # OpenAPI/Swagger docs
```

---

**This completes the package documentation. Each package serves a specific purpose in making the BikeShop platform functional and maintainable.**
