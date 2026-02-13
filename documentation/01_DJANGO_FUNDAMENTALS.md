# Django Fundamentals - Understanding the Framework

**Part 2 of Complete Documentation Series**

---

## 📋 Table of Contents

1. [What is Django?](#what-is-django)
2. [Django Project vs Apps](#django-project-vs-apps)
3. [manage.py - The Command Center](#managepy---the-command-center)
4. [settings.py - Configuration Hub](#settingspy---configuration-hub)
5. [urls.py - The Router](#urlspy---the-router)
6. [MVT Pattern Deep Dive](#mvt-pattern-deep-dive)
7. [Django ORM Explained](#django-orm-explained)

---

## 1. What is Django?

### Philosophy

Django follows these principles:

1. **Don't Repeat Yourself (DRY)** - Write code once, reuse everywhere
2. **Convention over Configuration** - Sensible defaults, less boilerplate
3. **Loose Coupling** - Components are independent
4. **Explicit is Better** - Clear code over magic

### Core Components

```python
# Django provides these out of the box:
- ORM (Database abstraction)
- Admin interface (Auto-generated)
- Authentication system
- Form handling
- Template engine
- URL routing
- Session management
- Security features (CSRF, XSS, SQL injection protection)
```

---

## 2. Django Project vs Apps

### Project = Container
**Project:** The entire website/application
- Contains settings, URLs, WSGI config
- One project per website

### Apps = Modular Components
**App:** A specific feature/functionality
- Reusable across projects
- Follows single responsibility principle

### Our Project Structure

```
bike_shop/              ← PROJECT (Container)
│
├── bike_shop/          ← Configuration package
│   ├── settings.py     ← Project-wide settings
│   ├── urls.py         ← Root URL configuration
│   └── wsgi.py         ← Web server gateway
│
└── apps/               ← APPS (Features)
    ├── accounts/       ← User management app
    ├── catalog/        ← Product catalog app
    ├── cart/           ← Shopping cart app
    ├── api/            ← REST API app
    └── ...
```

### Why This Separation?

**Example:** The `catalog` app handles products/categories
- Can be used in another e-commerce project
- Independent of authentication or cart
- Self-contained with its own models, views, tests

---

## 3. manage.py - The Command Center

### What is manage.py?

**Location:** `manage.py` (root directory)

```python
#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    # Set default settings module
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bike_shop.settings')
    
    try:
        # Import Django's management utility
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    
    # Execute command from terminal
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
```

### Line-by-Line Explanation

1. **`#!/usr/bin/env python`**
   - Shebang line (Unix systems)
   - Tells OS to use Python interpreter

2. **`os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bike_shop.settings')`**
   - Sets environment variable pointing to settings
   - Django knows where to find configuration
   - `'bike_shop.settings'` = `bike_shop/settings.py`

3. **`from django.core.management import execute_from_command_line`**
   - Imports Django's command executor
   - Handles all `python manage.py <command>` calls

4. **`execute_from_command_line(sys.argv)`**
   - Executes command from terminal
   - `sys.argv` = list of command arguments
   - Example: `['manage.py', 'runserver']`

### Common Commands

```bash
# Database operations
python manage.py makemigrations    # Detect model changes
python manage.py migrate           # Apply migrations to DB

# User management
python manage.py createsuperuser   # Create admin user

# Development
python manage.py runserver         # Start dev server (http://127.0.0.1:8000)
python manage.py runserver 0.0.0.0:8000  # Make accessible on network

# Shell access
python manage.py shell             # Interactive Python shell with Django loaded

# App management
python manage.py startapp myapp    # Create new Django app

# Static files
python manage.py collectstatic     # Collect static files for production

# Testing
python manage.py test              # Run all tests
python manage.py test accounts     # Run tests for specific app
```

---

## 4. settings.py - Configuration Hub

### What is settings.py?

**Location:** `bike_shop/settings.py`

This file controls **EVERYTHING** about your Django project.

### Key Sections Explained

#### A. Import and Environment Setup

```python
import os, sys
from dotenv import load_dotenv
load_dotenv()

from pathlib import Path
```

**What's happening:**
- `os, sys` - Operating system and system-specific functions
- `load_dotenv()` - Loads environment variables from `.env` file
  - Why? Keep secrets (passwords, API keys) out of code
  - Example: `SECRET_KEY = os.getenv('SECRET_KEY')`
- `Path` - Modern way to handle file paths (Python 3.4+)

#### B. Base Directory

```python
BASE_DIR = Path(__file__).resolve().parent.parent
```

**What's happening:**
- `__file__` - Current file (settings.py)
- `.resolve()` - Get absolute path
- `.parent.parent` - Go up two directories

**Result:**
```
/path/to/be-ecomm-affiliate/bike_shop/settings.py  ← __file__
/path/to/be-ecomm-affiliate/bike_shop/             ← .parent
/path/to/be-ecomm-affiliate/                       ← .parent.parent (BASE_DIR)
```

**Why?** All paths reference BASE_DIR for portability

#### C. Python Path Modification

```python
sys.path.insert(0, str(BASE_DIR / "apps"))
```

**What's happening:**
- Adds `apps/` directory to Python's import path
- **Before:** `from apps.accounts.models import User`
- **After:** `from accounts.models import User`
- Makes imports cleaner

#### D. Secret Key

```python
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-temporary-key...')
```

**What's happening:**
- Cryptographic key for Django security features
- Used for: sessions, cookies, CSRF tokens, password reset tokens
- **Production:** MUST be secret and unique
- **Development:** Default fallback key provided

#### E. Debug Mode

```python
DEBUG = True
```

**What's happening:**
- `True` - Show detailed error pages (development)
- `False` - Show generic error pages (production)
- **NEVER** set `DEBUG = True` in production (security risk)

#### F. Allowed Hosts

```python
ALLOWED_HOSTS = []
```

**What's happening:**
- Empty list = accept all hosts (DEBUG=True only)
- Production: `['yourdomain.com', 'www.yourdomain.com']`
- Security feature to prevent HTTP Host header attacks

#### G. Installed Apps

```python
INSTALLED_APPS = [
    # Django built-in apps
    'django.contrib.admin',          # Admin interface
    'django.contrib.auth',           # Authentication system
    'django.contrib.contenttypes',   # Content type framework
    'django.contrib.sessions',       # Session framework
    'django.contrib.messages',       # Messaging framework
    'django.contrib.staticfiles',    # Static file management

    # Third-party packages
    'rest_framework',                # Django REST Framework
    'corsheaders',                   # CORS headers for API
    
    # Our custom apps
    'accounts',                      # User management
    'catalog',                       # Products, categories
    'cart',                          # Shopping cart
    'core',                          # Shared models
    'orders',                        # Order management
    'promotions',                    # Discounts
    'api',                           # REST API
    'dashboard',                     # Admin dashboard
]
```

**What's happening:**
- Tells Django which apps to load
- Order matters! Apps loaded top-to-bottom
- Each app can have models, views, templates, static files

**Why order matters:**
```python
# ❌ WRONG - corsheaders MUST be before other middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # Should be here
]

# ✅ CORRECT
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # First!
    'django.middleware.security.SecurityMiddleware',
]
```

#### H. Custom User Model

```python
AUTH_USER_MODEL = 'accounts.User'
```

**What's happening:**
- Replaces Django's default `User` model
- Points to our custom `User` model in `accounts` app
- **MUST** be set before first migration
- Why? We need email as username, phone field, etc.

#### I. Middleware

```python
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',        # CORS handling
    'django.middleware.security.SecurityMiddleware', # Security
    'django.contrib.sessions.middleware.SessionMiddleware', # Sessions
    'django.middleware.common.CommonMiddleware',    # Common utilities
    'django.middleware.csrf.CsrfViewMiddleware',    # CSRF protection
    'django.contrib.auth.middleware.AuthenticationMiddleware', # Auth
    'django.contrib.messages.middleware.MessageMiddleware', # Messages
    'django.middleware.clickjacking.XFrameOptionsMiddleware', # Clickjacking
]
```

**What's happening:**
- Middleware = code that runs on EVERY request/response
- Processes requests before reaching views
- Processes responses before sending to client

**Request Flow:**
```
Request → Middleware 1 → Middleware 2 → ... → View → ... → Middleware 2 → Middleware 1 → Response
```

**Example - CORS Middleware:**
```
1. Request comes from http://localhost:3000
2. CorsMiddleware checks if origin is allowed
3. If yes, adds CORS headers to response
4. If no, blocks request
```

#### J. Database Configuration

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

**What's happening:**
- Defines database connection
- `ENGINE` - Database type (sqlite3, mysql, postgresql)
- `NAME` - Database file path (SQLite) or name (MySQL/PostgreSQL)

**MySQL Example (Commented Out):**
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'bikeshop_db',
        'USER': 'root',
        'PASSWORD': 'secret',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {"charset": "utf8mb4"},  # UTF-8 support
    }
}
```

#### K. REST Framework Configuration

```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_PAGINATION_CLASS': 'api.pagination.LaravelStylePagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
}
```

**Line-by-Line:**

1. **Authentication:**
   ```python
   'DEFAULT_AUTHENTICATION_CLASSES': [
       'rest_framework_simplejwt.authentication.JWTAuthentication',
   ]
   ```
   - How users prove identity
   - JWT = JSON Web Token (stateless authentication)
   - Every API request checks `Authorization: Bearer <token>` header

2. **Permissions:**
   ```python
   'DEFAULT_PERMISSION_CLASSES': [
       'rest_framework.permissions.AllowAny',
   ]
   ```
   - `AllowAny` = No authentication required by default
   - Individual views can override (e.g., profile requires auth)

3. **Pagination:**
   ```python
   'DEFAULT_PAGINATION_CLASS': 'api.pagination.LaravelStylePagination',
   'PAGE_SIZE': 20,
   ```
   - Splits large datasets into pages
   - Custom pagination mimics Laravel format
   - 20 items per page

4. **Filtering:**
   ```python
   'DEFAULT_FILTER_BACKENDS': [
       'django_filters.rest_framework.DjangoFilterBackend',  # ?category=bikes
       'rest_framework.filters.SearchFilter',                # ?search=helmet
       'rest_framework.filters.OrderingFilter',              # ?ordering=-price
   ]
   ```

#### L. JWT Configuration

```python
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=7),    # Token valid for 7 days
    'ROTATE_REFRESH_TOKENS': False,                # No refresh tokens
    'BLACKLIST_AFTER_ROTATION': False,             # No token blacklist
    'UPDATE_LAST_LOGIN': True,                     # Update last_login field
    'ALGORITHM': 'HS256',                          # HMAC-SHA256 algorithm
    'AUTH_HEADER_TYPES': ('Bearer',),              # "Authorization: Bearer <token>"
}
```

**Design Decision:**
- Single token, no refresh tokens
- Simpler for mobile apps
- Users re-login after 7 days

#### M. CORS Configuration

```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",      # React dev server
    "http://127.0.0.1:3000",      # Alternative localhost
]

CORS_ORIGIN_ALLOW_ALL = True     # Allow all (development only!)
CORS_ALLOW_CREDENTIALS = True    # Allow cookies/sessions
```

**What's CORS?**
- Cross-Origin Resource Sharing
- Browser security feature
- **Problem:** API at `localhost:8000`, frontend at `localhost:3000`
- **Solution:** Backend tells browser "allow requests from localhost:3000"

#### N. Static and Media Files

```python
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "static"]  # Where to find static files
STATIC_ROOT = BASE_DIR / "staticfiles"    # Where to collect for production

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / "media"           # User uploads go here
```

**Static vs Media:**
- **Static:** Your files (CSS, JS, images in code)
- **Media:** User uploads (product images, logos)

---

## 5. urls.py - The Router

### What is urls.py?

**Location:** `bike_shop/urls.py`

Routes incoming URLs to appropriate views.

### Code Breakdown

```python
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

# Custom redirect function
def redirect_to_dashboard_login(request):
    return redirect('dashboard:login')

urlpatterns = [
    # Django admin interface
    path('admin/', admin.site.urls),
    
    # Redirect accounts/login to dashboard login
    path('accounts/login/', redirect_to_dashboard_login),
    
    # Include API URLs
    path('api/', include('api.urls')),
    
    # Include dashboard URLs
    path('', include('dashboard.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
```

### URL Patterns Explained

**Pattern Syntax:**
```python
path('products/', ProductListView.as_view(), name='product-list')
│    │          │                            │
│    │          │                            └─ Reverse URL name
│    │          └─ View function/class
│    └─ URL pattern
└─ path() function
```

**Example Matching:**
```python
path('products/', ...)              # Matches: /products/
path('products/<int:id>/', ...)     # Matches: /products/123/
path('products/<slug:slug>/', ...)  # Matches: /products/helmet-abc/
```

### URL Include

```python
path('api/', include('api.urls'))
```

**What's happening:**
- Includes ALL URLs from `apps/api/urls.py`
- Prefix all with `api/`
- **Result:** 
  - `api/products/` → `apps/api/urls.py` → `ProductListView`
  - `api/cart/` → `apps/api/urls.py` → `CartView`

**Benefits:**
- Modular URL configuration
- Each app manages its own URLs
- Easy to reorganize

---

## 6. MVT Pattern Deep Dive

### Model-View-Template in Django

```
┌─────────────────────────────────────────────────────┐
│                   CLIENT REQUEST                     │
│              GET /api/products/?page=1              │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────┐
│                  1. URL ROUTING                      │
│  urls.py: path('products/', ProductListView)         │
└──────────────────────┬───────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────┐
│                   2. VIEW (Logic)                    │
│  - Authenticate user                                  │
│  - Parse query parameters                            │
│  - Query database                                     │
│  - Apply filters/pagination                          │
└──────────────────────┬───────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────┐
│                3. MODEL (Database)                   │
│  Product.objects.filter(is_active=True)              │
│  - ORM translates to SQL                             │
│  - Fetches data from database                        │
└──────────────────────┬───────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────┐
│              4. SERIALIZER (Transform)               │
│  ProductListSerializer(products, many=True)          │
│  - Convert Python objects to JSON                    │
│  - Add computed fields                               │
└──────────────────────┬───────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────┐
│                  5. RESPONSE                         │
│            JSON data sent to client                  │
└──────────────────────────────────────────────────────┘
```

---

## 7. Django ORM Explained

### What is ORM?

**Object-Relational Mapping** = Write Python, get SQL

### Example Comparison

**Python (Django ORM):**
```python
Product.objects.filter(category__slug='helmets', price__lt=10000)
```

**SQL (Generated Automatically):**
```sql
SELECT * FROM products 
INNER JOIN categories ON products.category_id = categories.id 
WHERE categories.slug = 'helmets' AND products.price < 10000;
```

### Common ORM Operations

```python
# Create
product = Product.objects.create(title='Helmet', price=5000)

# Read (single)
product = Product.objects.get(id=1)

# Read (multiple)
products = Product.objects.filter(is_active=True)

# Update
product.price = 6000
product.save()

# Delete
product.delete()

# Complex queries
Product.objects.filter(
    category__slug='helmets',
    price__gte=5000,
    price__lte=15000
).order_by('-created_at')[:10]
```

### QuerySet Chaining

```python
# Start with all products
qs = Product.objects.all()

# Add filters (lazy evaluation - no DB query yet)
qs = qs.filter(is_active=True)
qs = qs.filter(category__slug='helmets')
qs = qs.order_by('-price')

# Execute query (now hits database)
products = list(qs)  # or iterate: for p in qs
```

---

## Next Document

Continue to **02_MODELS_EXPLAINED.md** for detailed database model breakdowns.
