# BikeShop E-Commerce Platform - Complete Project Overview

**Documentation Date:** November 23, 2025  
**Project Type:** Django REST API Backend for E-Commerce  
**Purpose:** Backend API for a bike shop e-commerce platform with affiliate features

---

## 📋 Table of Contents

1. [Project Summary](#project-summary)
2. [Technology Stack](#technology-stack)
3. [Project Structure](#project-structure)
4. [Key Features](#key-features)
5. [Architecture Overview](#architecture-overview)
6. [Development Workflow](#development-workflow)

---

## 1. Project Summary

### What is This Project?

This is a **Django-based REST API backend** for a bike shop e-commerce platform. It provides a complete set of APIs for:

- **User Management:** Registration, authentication, profile management
- **Product Catalog:** Products, categories, brands with search and filtering
- **Shopping Cart:** Guest and authenticated user carts with session management
- **Order Management:** Order creation and tracking
- **Content Management:** Banners, featured sections for homepage
- **Admin Dashboard:** Custom admin interface for managing the platform

### Business Purpose

- **B2C E-Commerce:** Sell bike-related products (helmets, bikes, accessories)
- **Affiliate Features:** Track and manage affiliate marketing (future enhancement)
- **Multi-Tenant Support:** Can be extended for multiple vendors
- **Mobile-First:** API designed for mobile apps and web frontends

---

## 2. Technology Stack

### Core Framework
- **Django 5.2.7** - High-level Python web framework
  - Why? Mature, secure, batteries-included framework with ORM, admin panel
  - Philosophy: "Don't repeat yourself" (DRY), rapid development

### API Framework
- **Django REST Framework (DRF)** - Powerful toolkit for building Web APIs
  - Why? Industry standard for Django APIs, provides serializers, authentication
  - Features: Browsable API, authentication, permissions, throttling

### Database
- **SQLite3** (Development) - Lightweight file-based database
  - Why? No setup required, perfect for development and testing
  - Production: Can switch to MySQL/PostgreSQL via settings
- **Django ORM** - Object-Relational Mapping for database operations
  - Why? Database-agnostic, write Python instead of SQL

### Authentication
- **JWT (JSON Web Tokens)** via `djangorestframework-simplejwt`
  - Why? Stateless authentication, perfect for mobile/SPA apps
  - Token Lifetime: 7 days (configurable)
  - No refresh tokens (simplified approach)

### Key Python Packages

```toml
django = "*"                          # Web framework
djangorestframework = "*"             # REST API framework
djangorestframework-simplejwt = "*"   # JWT authentication
django-cors-headers = "*"             # Cross-Origin Resource Sharing
django-filter = "*"                   # Advanced filtering
pillow = "*"                          # Image processing
python-dotenv = "*"                   # Environment variables
mysqlclient = "*"                     # MySQL database adapter (optional)
psycopg2-binary = "*"                 # PostgreSQL adapter (optional)
```

### Frontend Technologies (Separate)
- **React/Next.js** - Assumed frontend framework (not in this repo)
- **Mobile Apps** - Can consume these APIs

---

## 3. Project Structure

```
be-ecomm-affiliate/
├── bike_shop/                 # Django project configuration
│   ├── settings.py           # Main settings file
│   ├── urls.py               # Root URL routing
│   ├── wsgi.py               # WSGI application entry point
│   └── asgi.py               # ASGI application (for async)
│
├── apps/                      # All Django applications
│   ├── accounts/             # User management & authentication
│   ├── api/                  # REST API endpoints & serializers
│   ├── cart/                 # Shopping cart functionality
│   ├── catalog/              # Products, categories, brands
│   ├── core/                 # Shared models (banners, sections)
│   ├── dashboard/            # Custom admin interface
│   ├── orders/               # Order management
│   ├── promotions/           # Discounts & promotions
│   └── reviews/              # Product reviews
│
├── templates/                 # HTML templates for admin dashboard
│   ├── admin/                # Custom admin templates
│   └── layouts/              # Reusable layout templates
│
├── static/                    # Static files (CSS, JS, images)
│   └── assets/               # Admin dashboard assets
│
├── media/                     # User-uploaded files (images)
│   ├── products/             # Product images
│   ├── categories/           # Category images
│   ├── brands/               # Brand logos
│   └── banners/              # Banner images
│
├── documentation/             # Project documentation (this folder)
├── development_logs/          # Implementation logs & guides
│
├── manage.py                  # Django management script
├── Pipfile                    # Dependency management
├── db.sqlite3                 # SQLite database file
└── README.md                  # Project README
```

### Why This Structure?

1. **Separation of Concerns:** Each app handles specific functionality
2. **Modularity:** Apps can be reused in other projects
3. **Scalability:** Easy to add new apps as features grow
4. **Django Convention:** Follows Django's recommended structure

---

## 4. Key Features

### ✅ Implemented Features

#### Authentication & User Management
- ✅ User registration with email/password
- ✅ JWT-based login/logout
- ✅ User profile management
- ✅ Password change
- ✅ Multiple address management
- ✅ Guest user support

#### Product Catalog
- ✅ Product listing with pagination
- ✅ Product detail pages
- ✅ Category hierarchy (parent/child)
- ✅ Brand management
- ✅ Product variants (size, color, etc.)
- ✅ Multiple product images
- ✅ Stock management
- ✅ Sale prices & discounts

#### Search & Filtering
- ✅ Product search by title/description
- ✅ Filter by category
- ✅ Filter by brand
- ✅ Filter by price range
- ✅ Filter by sale status
- ✅ Sorting (price, date, title)

#### Shopping Cart
- ✅ Guest cart (session-based)
- ✅ Authenticated user cart
- ✅ Add/update/remove items
- ✅ Cart merge on login
- ✅ Price snapshot (price at add time)
- ✅ Stock validation
- ✅ Cart persistence

#### Homepage Content
- ✅ Dynamic banners with images
- ✅ Featured product sections
- ✅ Category showcase
- ✅ Brand showcase
- ✅ Mobile-optimized images

#### Admin Dashboard
- ✅ Custom admin interface
- ✅ User management
- ✅ Order management
- ✅ Product management (via Django admin)
- ✅ Role-based access control

### 🚧 Future Features
- ⏳ Order placement & checkout
- ⏳ Payment gateway integration
- ⏳ Order tracking
- ⏳ Product reviews & ratings
- ⏳ Wishlist functionality
- ⏳ Coupon/promo code system
- ⏳ Email notifications
- ⏳ Affiliate tracking

---

## 5. Architecture Overview

### Architecture Pattern: MVT (Model-View-Template)

Django uses the **MVT pattern**, a variation of MVC:

```
┌─────────────┐
│   Client    │  (React/Mobile App)
│  (Frontend) │
└──────┬──────┘
       │ HTTP Request (JSON)
       ▼
┌─────────────────────────────┐
│      Django Backend         │
│  ┌───────────────────────┐  │
│  │   URLs (Routing)      │  │  ← Routes requests to views
│  └───────────┬───────────┘  │
│              ▼               │
│  ┌───────────────────────┐  │
│  │   Views (Logic)       │  │  ← Business logic
│  └───────────┬───────────┘  │
│              ▼               │
│  ┌───────────────────────┐  │
│  │  Serializers (DRF)    │  │  ← Data transformation
│  └───────────┬───────────┘  │
│              ▼               │
│  ┌───────────────────────┐  │
│  │   Models (ORM)        │  │  ← Database layer
│  └───────────┬───────────┘  │
│              ▼               │
│  ┌───────────────────────┐  │
│  │   Database            │  │  ← SQLite/MySQL/PostgreSQL
│  └───────────────────────┘  │
└─────────────────────────────┘
       │
       ▼ HTTP Response (JSON)
┌─────────────┐
│   Client    │
└─────────────┘
```

### Request Flow Example

**Example: User views product list**

1. **Client Request:**
   ```
   GET /api/products/?category=helmets&page=1
   ```

2. **URL Routing:** (`apps/api/urls.py`)
   ```python
   path('products/', ProductListView.as_view(), name='product-list')
   ```

3. **View Processing:** (`apps/api/views/catalog.py`)
   ```python
   class ProductListView(APIView):
       # Apply filters, pagination
       # Query database via ORM
   ```

4. **Database Query:** (Django ORM)
   ```python
   Product.objects.filter(category__slug='helmets', is_active=True)
   ```

5. **Serialization:** (`apps/api/serializers/catalog.py`)
   ```python
   ProductListSerializer(products, many=True)
   # Converts Python objects to JSON
   ```

6. **Response:**
   ```json
   {
     "data": [...],
     "meta": { "pagination": ... }
   }
   ```

---

## 6. Development Workflow

### Initial Setup

```bash
# 1. Clone repository
git clone <repository-url>

# 2. Install dependencies
pip install pipenv
pipenv install

# 3. Activate virtual environment
pipenv shell

# 4. Run migrations
python manage.py migrate

# 5. Create superuser
python manage.py createsuperuser

# 6. Run development server
python manage.py runserver
```

### Common Django Commands

```bash
# Create new app
python manage.py startapp <app_name>

# Make migrations (detect model changes)
python manage.py makemigrations

# Apply migrations (update database)
python manage.py migrate

# Create superuser (admin access)
python manage.py createsuperuser

# Run development server
python manage.py runserver

# Open Django shell (interactive Python)
python manage.py shell

# Collect static files (for production)
python manage.py collectstatic
```

### Development Cycle

1. **Define Models** → Database structure
2. **Create Migrations** → Schema changes
3. **Build Serializers** → API data format
4. **Write Views** → Business logic
5. **Configure URLs** → API routing
6. **Test APIs** → Verify functionality
7. **Document** → API documentation

---

## Key Design Decisions

### 1. Why JWT Authentication?
- **Stateless:** No server-side session storage
- **Scalable:** Works with multiple servers
- **Mobile-Friendly:** Easy to implement in mobile apps
- **7-Day Tokens:** Balance between security and UX

### 2. Why Separate API App?
- **Clean Separation:** Frontend/backend completely independent
- **Multiple Frontends:** Web, mobile can use same API
- **Version Control:** Can version API (v1, v2)

### 3. Why Guest Cart?
- **User Experience:** Users can shop without account
- **Conversion:** Reduce friction in shopping
- **Session-Based:** Uses Django sessions

### 4. Why Custom Admin Dashboard?
- **Branding:** Matches company branding
- **UX:** Better than default Django admin
- **Features:** Tailored to business needs

### 5. Why SQLite for Development?
- **Zero Setup:** Works immediately
- **Portable:** Database is single file
- **Fast:** Perfect for development
- **Production:** Switch to PostgreSQL/MySQL

---

## Next Steps

Continue reading the documentation in order:

1. ✅ **00_PROJECT_OVERVIEW.md** (You are here)
2. 📄 **01_DJANGO_FUNDAMENTALS.md** - Understanding Django basics
3. 📄 **02_MODELS_EXPLAINED.md** - Database models in detail
4. 📄 **03_API_ARCHITECTURE.md** - REST API design
5. 📄 **04_AUTHENTICATION_FLOW.md** - JWT & user management
6. 📄 **05_CART_SYSTEM.md** - Shopping cart implementation
7. 📄 **06_ADMIN_DASHBOARD.md** - Custom admin interface
8. 📄 **07_DEPLOYMENT_GUIDE.md** - Production deployment

---

**This documentation explains the entire project line-by-line. Each subsequent document dives deeper into specific components.**
