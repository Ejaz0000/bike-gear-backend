# Quick Reference Guide - BikeShop E-Commerce

**Quick answers to common questions**

---

## 🚀 Getting Started

### First Time Setup
```bash
# 1. Navigate to project
cd be-ecomm-affiliate

# 2. Install dependencies
pipenv install

# 3. Activate environment
pipenv shell

# 4. Run migrations
python manage.py migrate

# 5. Create admin user
python manage.py createsuperuser

# 6. Start server
python manage.py runserver
```

### Access Points
- **API:** http://localhost:8000/api/
- **Admin Dashboard:** http://localhost:8000/dashboard/
- **Django Admin:** http://localhost:8000/admin/

---

## 📁 Project Structure Quick Map

```
bike_shop/          → Configuration (settings, urls)
apps/
  ├── accounts/     → Users, addresses
  ├── api/          → REST API endpoints
  ├── catalog/      → Products, categories, brands
  ├── cart/         → Shopping cart
  ├── core/         → Banners, featured sections
  ├── dashboard/    → Custom admin interface
  ├── orders/       → Order management
  └── reviews/      → Product reviews
templates/          → HTML templates
static/             → CSS, JS, images (admin dashboard)
media/              → User uploads (product images)
documentation/      → This folder
```

---

## 🔑 Key Files

| File | Purpose |
|------|---------|
| `manage.py` | Django command-line tool |
| `bike_shop/settings.py` | All configuration |
| `bike_shop/urls.py` | Root URL routing |
| `apps/api/urls.py` | API URL patterns |
| `apps/api/views/` | API business logic |
| `apps/api/serializers/` | Data transformation |
| `apps/*/models.py` | Database models |
| `Pipfile` | Dependencies |

---

## 💾 Database

### Current Setup
- **Development:** SQLite (file: `db.sqlite3`)
- **Production Ready:** MySQL/PostgreSQL

### Common Operations
```bash
# Create migration after model change
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Reset database (CAUTION!)
rm db.sqlite3
python manage.py migrate
python manage.py createsuperuser

# Open database shell
python manage.py dbshell
```

---

## 🔐 Authentication

### How It Works
```
1. User logs in: POST /api/auth/login/
2. Server returns JWT token
3. Client stores token
4. Client sends with each request:
   Authorization: Bearer <token>
5. Server validates token
```

### Token Lifetime
- **7 days** (configurable in settings.py)
- No refresh tokens (simplified)

### Protected Endpoints
```python
# Require authentication
permission_classes = [IsAuthenticated]

# Allow anyone
permission_classes = [AllowAny]
```

---

## 🛍️ Key Models

### User
```python
# Access: from accounts.models import User
fields: email, name, phone, is_active, is_staff
login with: email (not username)
```

### Product
```python
# Access: from catalog.models import Product
fields: title, slug, price, sale_price, stock, description
relationships: category, brand, images, variants
```

### Cart
```python
# Access: from cart.models import Cart
fields: user (nullable), session_key
relationships: items
supports: guest carts (session-based)
```

### Category
```python
# Access: from catalog.models import Category
fields: name, slug, parent, image
hierarchical: parent-child relationships
```

---

## 🌐 API Endpoints Quick Reference

### Authentication
```
POST   /api/auth/register/        Register new user
POST   /api/auth/login/           Login (get token)
GET    /api/auth/profile/         Get user profile [AUTH]
PATCH  /api/auth/profile/         Update profile [AUTH]
POST   /api/auth/change-password/ Change password [AUTH]
```

### Products
```
GET    /api/products/             List products
GET    /api/products/{slug}/      Product detail
```

### Categories
```
GET    /api/categories/           List categories
GET    /api/categories/{slug}/    Category detail
```

### Brands
```
GET    /api/brands/               List brands
GET    /api/brands/{slug}/        Brand detail
```

### Cart
```
GET    /api/cart/                 Get cart
POST   /api/cart/items/           Add to cart
PATCH  /api/cart/items/{id}/      Update quantity
DELETE /api/cart/items/{id}/      Remove item
DELETE /api/cart/clear/           Clear cart
```

### Homepage
```
GET    /api/homepage/             Get all homepage data
```

---

## 🔍 Filtering & Search

### Product List Filters
```
?page=2                    Pagination
?page_size=50              Items per page
?category=helmets          Filter by category
?brand=giro                Filter by brand
?min_price=1000            Minimum price
?max_price=5000            Maximum price
?search=mountain           Search title/description
?on_sale=true              Sale products only
?ordering=-price           Sort descending by price
?ordering=created_at       Sort ascending by date
```

### Example
```
GET /api/products/?category=helmets&brand=giro&min_price=1000&max_price=5000&ordering=-price
```

---

## 📦 Packages

### Core
- `django` - Web framework
- `djangorestframework` - API framework
- `djangorestframework-simplejwt` - JWT auth

### Features
- `django-cors-headers` - CORS support
- `django-filter` - API filtering
- `pillow` - Image processing

### Database
- `mysqlclient` - MySQL adapter (optional)
- `psycopg2-binary` - PostgreSQL adapter (optional)

### Utilities
- `python-dotenv` - Environment variables

---

## 🛠️ Common Tasks

### Add New API Endpoint

1. **Define model** (if needed)
   ```python
   # apps/catalog/models.py
   class NewModel(models.Model):
       name = models.CharField(max_length=200)
   ```

2. **Create migration**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

3. **Create serializer**
   ```python
   # apps/api/serializers/
   class NewModelSerializer(serializers.ModelSerializer):
       class Meta:
           model = NewModel
           fields = '__all__'
   ```

4. **Create view**
   ```python
   # apps/api/views/
   class NewModelView(APIView):
       def get(self, request):
           items = NewModel.objects.all()
           serializer = NewModelSerializer(items, many=True)
           return Response(serializer.data)
   ```

5. **Add URL**
   ```python
   # apps/api/urls.py
   path('new-endpoint/', NewModelView.as_view())
   ```

### Modify Database Model

1. **Edit model**
   ```python
   # Add/modify field
   new_field = models.CharField(max_length=100)
   ```

2. **Create migration**
   ```bash
   python manage.py makemigrations
   ```

3. **Review migration** (optional)
   ```bash
   python manage.py sqlmigrate app_name migration_number
   ```

4. **Apply migration**
   ```bash
   python manage.py migrate
   ```

### Add Authentication to Endpoint

```python
from rest_framework.permissions import IsAuthenticated

class ProtectedView(APIView):
    permission_classes = [IsAuthenticated]  # ← Add this
    
    def get(self, request):
        user = request.user  # Authenticated user
        # ...
```

---

## 🐛 Debugging

### Check Errors
```bash
# View recent errors in terminal
# Django shows detailed error pages when DEBUG=True
```

### Django Shell
```bash
python manage.py shell

# Interactive Python with Django loaded
>>> from catalog.models import Product
>>> Product.objects.all()
>>> # Test queries, check data
```

### Database Queries
```bash
# See SQL queries being executed
# Add to settings.py temporarily:

LOGGING = {
    'version': 1,
    'handlers': {
        'console': {'class': 'logging.StreamHandler'}
    },
    'loggers': {
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG'
        }
    }
}
```

---

## ⚡ Performance Tips

### Database Queries
```python
# ❌ Bad - N+1 query problem
products = Product.objects.all()
for p in products:
    print(p.category.name)  # Database query per product

# ✅ Good - Use select_related
products = Product.objects.select_related('category', 'brand')
for p in products:
    print(p.category.name)  # No extra queries

# ✅ Good - Use prefetch_related for reverse FKs
products = Product.objects.prefetch_related('images', 'variants')
```

### API Responses
```python
# ✅ Only select needed fields
Product.objects.only('id', 'title', 'price')

# ✅ Add database indexes
class Meta:
    indexes = [
        models.Index(fields=['slug']),
        models.Index(fields=['is_active', '-created_at']),
    ]
```

---

## 🔒 Security Checklist

### Development
- ✅ DEBUG = True
- ✅ SECRET_KEY can be simple
- ✅ CORS_ALLOW_ALL = True (for testing)
- ✅ SQLite database

### Production
- ⚠️ DEBUG = False
- ⚠️ SECRET_KEY must be unique and secret
- ⚠️ CORS_ALLOWED_ORIGINS specific domains
- ⚠️ Use PostgreSQL/MySQL
- ⚠️ Use environment variables
- ⚠️ HTTPS only
- ⚠️ Set ALLOWED_HOSTS

---

## 📚 Documentation Reference

For detailed explanations, see:

- **Project overview:** `00_PROJECT_OVERVIEW.md`
- **Django basics:** `01_DJANGO_FUNDAMENTALS.md`
- **Models explained:** `02_MODELS_DATABASE.md`
- **API architecture:** `03_API_ARCHITECTURE.md`
- **All packages:** `09_PACKAGES_EXPLAINED.md`

---

## 🆘 Common Issues

### Issue: Can't import Django
```bash
# Solution: Activate virtual environment
pipenv shell
```

### Issue: Database error
```bash
# Solution: Run migrations
python manage.py migrate
```

### Issue: Admin CSS not loading
```bash
# Solution: Collect static files
python manage.py collectstatic
```

### Issue: CORS error in browser
```bash
# Check CORS_ALLOWED_ORIGINS in settings.py
# Ensure frontend URL is listed
```

### Issue: 401 Unauthorized
```bash
# Check token in Authorization header
# Ensure token hasn't expired (7 days)
# Verify token format: Bearer <token>
```

---

## 📞 Need More Help?

- Read full documentation in `documentation/` folder
- Check `development_logs/` for implementation details
- Review `API_ENDPOINTS_LIST.md` for complete API reference

---

**This quick reference covers 80% of daily tasks. For deeper understanding, read the full documentation.**
