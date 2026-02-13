# 08 - Admin Dashboard System

**Last Updated:** November 23, 2025

This guide covers the custom admin dashboard system built for managing the BikeShop e-commerce platform.

---

## 📋 Table of Contents

1. [Dashboard Overview](#dashboard-overview)
2. [Authentication System](#authentication-system)
3. [Dashboard Home](#dashboard-home)
4. [User Management](#user-management)
5. [Catalog Management](#catalog-management)
6. [Order Management](#order-management)
7. [Content Management](#content-management)
8. [Template Structure](#template-structure)
9. [URL Configuration](#url-configuration)
10. [Security & Permissions](#security--permissions)

---

## Dashboard Overview

### What is the Admin Dashboard?

The admin dashboard is a **custom-built** web interface for managing the e-commerce platform. It's **separate from Django's default admin** and provides a tailored experience for:

- Managing users and their permissions
- Creating and editing products, categories, brands
- Processing orders and updating order status
- Managing homepage banners and featured sections
- Viewing analytics and reports

### Why Custom Dashboard?

```
Django Default Admin       vs.       Custom Dashboard
├── Generic interface               ├── Branded UI
├── Limited customization           ├── Tailored workflows
├── Developer-focused               ├── User-friendly
└── Standard layout                 └── Modern design
```

**Advantages:**
- ✅ Full control over UI/UX
- ✅ Custom workflows for e-commerce
- ✅ Better user experience
- ✅ Integration with frontend design
- ✅ Role-based views

### Access Points

```
Admin Dashboard: http://localhost:8000/
Login Page: http://localhost:8000/login/
API Access: http://localhost:8000/api/

Note: The root URL (/) redirects to the dashboard
```

---

## Authentication System

### Admin Login

**File:** `apps/dashboard/views.py`

```python
def admin_login(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('dashboard:dashboard')
        else:
            messages.error(request, 'Access denied. Staff privileges required.')
            logout(request)
    # Check if user is already authenticated
    # If yes and is staff → redirect to dashboard
    # If yes but not staff → show error and logout
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        # authenticate(): Django's built-in function
        # Validates credentials against database
        
        if user and user.is_staff:
            login(request, user)
            # login(): Creates session for user
            # Session stored in cookies
            
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('dashboard:dashboard')
            # Redirect to requested page or dashboard
        else:
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'admin/auth/login.html')
```

**Login Flow:**

```
1. User visits /login/
   ↓
2. Enter email (used as username) & password
   ↓
3. System checks:
   - Valid credentials?
   - is_staff = True?
   ↓
4a. Success → Redirect to dashboard
4b. Failure → Show error message
```

**Template:** `templates/admin/auth/login.html`

```html
<form method="POST" action="{% url 'dashboard:login' %}">
    {% csrf_token %}
    <input type="email" name="username" placeholder="Email" required>
    <input type="password" name="password" placeholder="Password" required>
    <button type="submit">Login</button>
</form>
```

**Security Features:**

1. **CSRF Protection**: `{% csrf_token %}` prevents cross-site attacks
2. **Staff Check**: Only `is_staff=True` users can access
3. **Session Management**: Automatic logout after inactivity
4. **Next URL**: Preserves intended destination after login

---

### Admin Logout

```python
@login_required
def admin_logout(request):
    logout(request)
    # Clears session data
    # Removes authentication cookies
    return redirect('dashboard:login')
```

---

### Custom Decorator: `admin_required`

**File:** `apps/dashboard/decorators.py`

```python
from functools import wraps
from django.shortcuts import redirect
from django.urls import reverse

def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse('dashboard:login'))
        # Check 1: Is user logged in?
        
        if not request.user.is_staff:
            return redirect(reverse('dashboard:login'))
        # Check 2: Is user a staff member?
        
        return view_func(request, *args, **kwargs)
        # Passed both checks → execute view
    return _wrapped_view
```

**Usage:**

```python
from django.contrib.auth.decorators import user_passes_test
from dashboard.decorators import admin_required

@user_passes_test(admin_required)
def protected_view(request):
    # This view is only accessible to staff members
    return render(request, 'admin/page.html')
```

**Why Two Decorators?**

```python
# Option 1: Django's built-in
@login_required
@user_passes_test(lambda u: u.is_staff)
def view(request):
    pass

# Option 2: Custom decorator (cleaner)
@user_passes_test(admin_required)
def view(request):
    pass
```

---

## Dashboard Home

### Dashboard Statistics

**File:** `apps/dashboard/views.py`

```python
@user_passes_test(admin_required)
def admin_dashboard(request):
    """Dashboard view with key metrics, top selling products, and low stock alerts"""
    from django.utils import timezone
    from catalog.models import Product, ProductVariant
    from orders.models import OrderItem
    
    # Get today's date
    today = timezone.now().date()
    
    # Statistics
    total_orders = Order.objects.count()
    # Count all orders in database
    
    total_customers = User.objects.filter(is_staff=False).count()
    # Count non-staff users (regular customers)
    
    todays_orders = Order.objects.filter(created_at__date=today).count()
    # Count orders created today
    # created_at__date: Extract date part from datetime
    
    total_products = Product.objects.filter(is_active=True).count()
    # Count active products only
    
    # Top 5 selling products (based on order items quantity)
    top_selling_products = Product.objects.annotate(
        total_sold=Sum('variants__orderitem__quantity')
    ).filter(total_sold__gt=0).order_by('-total_sold')[:5]
    # annotate(): Add calculated field
    # Sum('variants__orderitem__quantity'): Total quantity sold
    # Follows relationships: Product → Variant → OrderItem → quantity
    # filter(total_sold__gt=0): Only products with sales
    # order_by('-total_sold'): Highest sales first
    # [:5]: Limit to top 5
    
    # Low stock products (variants with stock <= 10)
    low_stock_threshold = 10
    low_stock_products = ProductVariant.objects.select_related('product').filter(
        stock__lte=low_stock_threshold,
        is_active=True
    ).order_by('stock')[:10]
    # select_related('product'): JOIN with product table (optimization)
    # stock__lte: Less than or equal to threshold
    # order_by('stock'): Lowest stock first
    
    context = {
        'total_orders': total_orders,
        'total_customers': total_customers,
        'todays_orders': todays_orders,
        'total_products': total_products,
        'top_selling_products': top_selling_products,
        'low_stock_products': low_stock_products,
        'low_stock_threshold': low_stock_threshold,
    }
    return render(request, 'admin/modules/dashboard/index.html', context)
```

**Dashboard Template:** `templates/admin/modules/dashboard/index.html`

```html
<!-- Statistics Cards -->
<div class="row">
    <div class="col-md-3">
        <div class="card">
            <div class="card-body">
                <h6>Total Orders</h6>
                <h2>{{ total_orders }}</h2>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card">
            <div class="card-body">
                <h6>Total Customers</h6>
                <h2>{{ total_customers }}</h2>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card">
            <div class="card-body">
                <h6>Today's Orders</h6>
                <h2>{{ todays_orders }}</h2>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card">
            <div class="card-body">
                <h6>Active Products</h6>
                <h2>{{ total_products }}</h2>
            </div>
        </div>
    </div>
</div>

<!-- Top Selling Products -->
<div class="card mt-4">
    <div class="card-header">
        <h5>Top Selling Products</h5>
    </div>
    <div class="card-body">
        <table class="table">
            <thead>
                <tr>
                    <th>Product</th>
                    <th>Total Sold</th>
                </tr>
            </thead>
            <tbody>
                {% for product in top_selling_products %}
                <tr>
                    <td>{{ product.title }}</td>
                    <td>{{ product.total_sold }} units</td>
                </tr>
                {% empty %}
                <tr>
                    <td colspan="2">No sales data available</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>

<!-- Low Stock Alert -->
<div class="card mt-4">
    <div class="card-header bg-warning">
        <h5>Low Stock Alert (≤ {{ low_stock_threshold }} units)</h5>
    </div>
    <div class="card-body">
        <table class="table">
            <thead>
                <tr>
                    <th>Product</th>
                    <th>SKU</th>
                    <th>Stock</th>
                    <th>Action</th>
                </tr>
            </thead>
            <tbody>
                {% for variant in low_stock_products %}
                <tr>
                    <td>{{ variant.product.title }}</td>
                    <td>{{ variant.sku }}</td>
                    <td>
                        <span class="badge {% if variant.stock == 0 %}bg-danger{% else %}bg-warning{% endif %}">
                            {{ variant.stock }} units
                        </span>
                    </td>
                    <td>
                        <a href="{% url 'dashboard:variant_edit' variant.id %}" class="btn btn-sm btn-primary">
                            Restock
                        </a>
                    </td>
                </tr>
                {% empty %}
                <tr>
                    <td colspan="4">All products have sufficient stock</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>
```

---

## User Management

### List Users

**Endpoint:** `/users/`

```python
@user_passes_test(admin_required)
def user_list(request):
    """Display list of all users with search and filter"""
    users = User.objects.all().order_by('-date_joined')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        users = users.filter(
            Q(email__icontains=search_query) |
            Q(name__icontains=search_query) |
            Q(phone__icontains=search_query)
        )
    # Q objects: OR condition
    # email__icontains: Case-insensitive contains
    # Example: search="john" matches "John Doe" or "john@example.com"
    
    # Filter by staff status
    is_staff = request.GET.get('is_staff', '')
    if is_staff:
        users = users.filter(is_staff=is_staff == 'true')
    # is_staff='true' → show only staff
    # is_staff='false' → show only customers
    
    # Filter by active status
    is_active = request.GET.get('is_active', '')
    if is_active:
        users = users.filter(is_active=is_active == 'true')
    
    context = {
        'users': users,
        'search_query': search_query,
        'is_staff': is_staff,
        'is_active': is_active,
    }
    return render(request, 'admin/modules/users/list.html', context)
```

**Filter Examples:**

```
# All users
GET /users/

# Search by name or email
GET /users/?search=john

# Only staff members
GET /users/?is_staff=true

# Only active customers
GET /users/?is_staff=false&is_active=true

# Combined filters
GET /users/?search=john&is_staff=false&is_active=true
```

---

### Add User

**Endpoint:** `/users/add/`

```python
@user_passes_test(admin_required)
def user_add(request):
    """Add new user"""
    if request.method == 'POST':
        email = request.POST.get('email')
        name = request.POST.get('name')
        phone = request.POST.get('phone', '')
        password = request.POST.get('password')
        is_staff = request.POST.get('is_staff') == 'on'
        # Checkbox: 'on' if checked, None if unchecked
        
        is_active = request.POST.get('is_active', 'on') == 'on'
        # Default to True if not specified
        
        # Validation
        if not email or not name or not password:
            messages.error(request, 'Email, name, and password are required.')
            return render(request, 'admin/modules/users/add.html', {
                'email': email,
                'name': name,
                'phone': phone,
                'is_staff': is_staff,
                'is_active': is_active,
            })
        # Preserve form data on error
        
        # Check if user exists
        if User.objects.filter(email=email).exists():
            messages.error(request, 'A user with this email already exists.')
            return render(request, 'admin/modules/users/add.html', {...})
        
        try:
            user = User.objects.create_user(
                email=email,
                password=password,
                name=name,
                phone=phone if phone else '',
            )
            # create_user(): Hashes password automatically
            # Never store plain text passwords!
            
            user.is_staff = is_staff
            user.is_active = is_active
            user.save()
            
            messages.success(request, f'User "{user.name}" created successfully!')
            return redirect('dashboard:user_list')
        except Exception as e:
            messages.error(request, f'Error creating user: {str(e)}')
    
    return render(request, 'admin/modules/users/add.html')
```

---

### Edit User

**Endpoint:** `/users/{id}/edit/`

```python
@user_passes_test(admin_required)
def user_edit(request, pk):
    """Edit existing user"""
    user = get_object_or_404(User, pk=pk)
    # get_object_or_404: Returns object or 404 error
    
    if request.method == 'POST':
        user.name = request.POST.get('name', user.name)
        user.email = request.POST.get('email', user.email)
        user.phone = request.POST.get('phone', '')
        user.is_staff = request.POST.get('is_staff') == 'on'
        user.is_active = request.POST.get('is_active') == 'on'
        
        # Update password if provided
        new_password = request.POST.get('new_password', '')
        if new_password:
            user.set_password(new_password)
        # set_password(): Hashes the password
        # Only update if new password provided
        
        try:
            user.save()
            messages.success(request, f'User "{user.name}" updated successfully!')
            return redirect('dashboard:user_list')
        except Exception as e:
            messages.error(request, f'Error updating user: {str(e)}')
    
    context = {
        'user_obj': user,
        'title': f'Edit User: {user.name}',
    }
    return render(request, 'admin/modules/users/edit.html', context)
```

---

### Delete User

**Endpoint:** `/users/{id}/delete/`

```python
@user_passes_test(admin_required)
def user_delete(request, pk):
    """Delete user with confirmation"""
    user_obj = get_object_or_404(User, pk=pk)
    
    # Prevent deleting yourself
    if user_obj == request.user:
        messages.error(request, 'You cannot delete your own account.')
        return redirect('dashboard:user_list')
    # Safety check: Admin can't delete themselves
    
    if request.method == 'POST':
        user_name = user_obj.name
        user_email = user_obj.email
        try:
            user_obj.delete()
            # CASCADE delete: Also deletes related addresses, orders, etc.
            messages.success(request, f'User "{user_name}" ({user_email}) deleted successfully!')
            return redirect('dashboard:user_list')
        except Exception as e:
            messages.error(request, f'Error deleting user: {str(e)}')
            return redirect('dashboard:user_list')
    
    context = {
        'user_obj': user_obj,
    }
    return render(request, 'admin/modules/users/delete.html', context)
```

**Delete Confirmation Template:**

```html
<form method="POST">
    {% csrf_token %}
    <h3>Are you sure you want to delete this user?</h3>
    <p>User: {{ user_obj.name }} ({{ user_obj.email }})</p>
    <p class="text-danger">
        <strong>Warning:</strong> This will also delete:
        <ul>
            <li>All addresses</li>
            <li>All orders</li>
            <li>Cart items</li>
        </ul>
        This action cannot be undone.
    </p>
    <button type="submit" class="btn btn-danger">Yes, Delete</button>
    <a href="{% url 'dashboard:user_list' %}" class="btn btn-secondary">Cancel</a>
</form>
```

---

## Catalog Management

### Category Management

**List Categories:** `/categories/`

```python
@user_passes_test(admin_required)
def category_list(request):
    """Display list of all categories with search and filter"""
    categories = Category.objects.select_related('parent').all()
    # select_related('parent'): JOIN parent category (optimization)
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        categories = categories.filter(name__icontains=search_query)
    
    # Filter by active status
    is_active = request.GET.get('is_active', '')
    if is_active:
        categories = categories.filter(is_active=is_active == 'true')
    
    # Filter by parent
    parent_id = request.GET.get('parent', '')
    if parent_id:
        if parent_id == 'none':
            categories = categories.filter(parent__isnull=True)
            # Top-level categories only
        else:
            categories = categories.filter(parent_id=parent_id)
            # Subcategories of specific parent
    
    context = {
        'categories': categories,
        'search_query': search_query,
        'is_active': is_active,
        'parent_id': parent_id,
        'all_categories': Category.objects.filter(parent__isnull=True),  # For filter dropdown
    }
    return render(request, 'admin/modules/categories/list.html', context)
```

**Add Category:** `/categories/add/`

```python
@user_passes_test(admin_required)
def category_add(request):
    """Add new category"""
    from catalog.forms import CategoryForm
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        # request.FILES: Handle file uploads (images)
        
        if form.is_valid():
            category = form.save()
            # save(): Creates database record
            # Auto-generates slug if not provided
            
            messages.success(request, f'Category "{category.name}" created successfully!')
            return redirect('dashboard:category_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CategoryForm()
    
    context = {
        'form': form,
        'title': 'Add Category',
    }
    return render(request, 'admin/modules/categories/add.html', context)
```

**Edit Category:** `/categories/{id}/edit/`

**Delete Category:** `/categories/{id}/delete/`

```python
@user_passes_test(admin_required)
def category_delete(request, pk):
    """Delete category with confirmation"""
    category = get_object_or_404(Category, pk=pk)
    
    # Check if category has children
    has_children = category.children.exists()
    has_products = category.products.exists()
    # Safety checks before deletion
    
    if request.method == 'POST':
        category_name = category.name
        try:
            category.delete()
            # CASCADE: Also deletes children categories!
            # Products set to NULL (not deleted)
            messages.success(request, f'Category "{category_name}" deleted successfully!')
            return redirect('dashboard:category_list')
        except Exception as e:
            messages.error(request, f'Error deleting category: {str(e)}')
    
    context = {
        'category': category,
        'has_children': has_children,
        'has_products': has_products,
        'children_count': category.children.count(),
        'products_count': category.products.count(),
    }
    return render(request, 'admin/modules/categories/delete.html', context)
```

---

### Product Management

**List Products:** `/products/`

```python
@user_passes_test(admin_required)
def product_list(request):
    """Display list of all products with search and filters"""
    products = Product.objects.select_related('category', 'brand').prefetch_related('images').all()
    # Optimize queries: JOIN category/brand, prefetch images
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        products = products.filter(title__icontains=search_query)
    
    # Filter by category
    category_id = request.GET.get('category', '')
    if category_id:
        products = products.filter(category_id=category_id)
    
    # Filter by brand
    brand_id = request.GET.get('brand', '')
    if brand_id:
        products = products.filter(brand_id=brand_id)
    
    # Filter by active status
    is_active = request.GET.get('is_active', '')
    if is_active:
        products = products.filter(is_active=is_active == 'true')
    
    context = {
        'products': products,
        'search_query': search_query,
        'is_active': is_active,
        'category_id': category_id,
        'brand_id': brand_id,
        'categories': Category.objects.all(),
        'brands': Brand.objects.all(),
    }
    return render(request, 'admin/modules/products/list.html', context)
```

**Add Product with Images:** `/products/add/`

```python
@user_passes_test(admin_required)
def product_add(request):
    """Add new product with images"""
    from catalog.forms import ProductForm
    from catalog.models import ProductImage
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            
            # Handle multiple image uploads with positions
            images = request.FILES.getlist('images')
            # getlist(): Get all files from input with name="images"
            
            positions = request.POST.getlist('image_positions')
            # Get position values for each image
            
            for idx, image in enumerate(images):
                # Use provided position or default to index
                position = int(positions[idx]) if idx < len(positions) else idx
                ProductImage.objects.create(
                    product=product,
                    image=image,
                    position=position,
                    alt_text=f"{product.title} - Image {position + 1}"
                )
            
            messages.success(request, f'Product "{product.title}" created successfully!')
            return redirect('dashboard:product_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProductForm()
    
    context = {
        'form': form,
        'title': 'Add Product',
        'categories': Category.objects.all(),
        'brands': Brand.objects.all(),
    }
    return render(request, 'admin/modules/products/add.html', context)
```

**Edit Product:** `/products/{id}/edit/`

```python
@user_passes_test(admin_required)
def product_edit(request, pk):
    """Edit existing product"""
    from catalog.models import ProductImage
    
    product = get_object_or_404(Product, pk=pk)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = form.save()
            
            # Handle new image uploads
            images = request.FILES.getlist('images')
            positions = request.POST.getlist('image_positions')
            
            if images:
                for idx, image in enumerate(images):
                    if idx < len(positions):
                        position = int(positions[idx])
                    else:
                        # Calculate next available position
                        max_position = product.images.aggregate(max_pos=Max('position'))['max_pos'] or -1
                        position = max_position + 1
                    
                    ProductImage.objects.create(
                        product=product,
                        image=image,
                        position=position,
                        alt_text=f"{product.title} - Image {position + 1}"
                    )
            
            # Handle image deletions
            delete_images = request.POST.getlist('delete_images')
            if delete_images:
                ProductImage.objects.filter(id__in=delete_images).delete()
            # Checkbox values of images to delete
            
            messages.success(request, f'Product "{product.title}" updated successfully!')
            return redirect('dashboard:product_list')
    else:
        form = ProductForm(instance=product)
    
    context = {
        'form': form,
        'product': product,
        'title': f'Edit Product: {product.title}',
        'product_images': product.images.all().order_by('position'),
    }
    return render(request, 'admin/modules/products/edit.html', context)
```

---

### Variant Management

**List Variants:** `/products/{product_id}/variants/`

**Add Variant:** `/products/{product_id}/variants/add/`

```python
@user_passes_test(admin_required)
def variant_add(request, product_id):
    """Add new variant to a product"""
    from catalog.forms import ProductVariantForm
    from catalog.models import AttributeType, AttributeValue, VariantAttribute
    
    product = get_object_or_404(Product, pk=product_id)
    
    if request.method == 'POST':
        form = ProductVariantForm(request.POST)
        if form.is_valid():
            variant = form.save(commit=False)
            # commit=False: Don't save to DB yet
            variant.product = product
            # Assign parent product
            variant.save()
            # Now save to DB
            
            # Handle attribute assignments
            attribute_types = AttributeType.objects.all()
            for attr_type in attribute_types:
                attr_value_id = request.POST.get(f'attribute_{attr_type.id}')
                # Example: attribute_1 (Size), attribute_2 (Color)
                
                if attr_value_id:
                    try:
                        attr_value = AttributeValue.objects.get(id=attr_value_id, attribute_type=attr_type)
                        VariantAttribute.objects.create(
                            product_variant=variant,
                            attribute_value=attr_value
                        )
                        # Link variant to attribute value
                    except AttributeValue.DoesNotExist:
                        pass
            
            messages.success(request, f'Variant "{variant.sku}" created successfully')
            return redirect('dashboard:variant_list', product_id=product.id)
    else:
        # Pre-fill with product defaults
        initial = {
            'price': product.price,
            'sale_price': product.sale_price,
            'weight': product.weight,
            'stock': 0,
        }
        form = ProductVariantForm(initial=initial)
    
    # Get all attribute types and their values for selection
    attribute_types = AttributeType.objects.prefetch_related('values').all()
    
    return render(request, 'admin/modules/variants/add.html', {
        'product': product,
        'form': form,
        'attribute_types': attribute_types,
    })
```

---

## Order Management

### List Orders

**Endpoint:** `/orders/`

```python
@user_passes_test(admin_required)
def order_list(request):
    """Display all orders with filters"""
    orders = Order.objects.select_related('user').prefetch_related('items').all().order_by('-created_at')
    
    # Filter by status
    status = request.GET.get('status', '')
    if status:
        orders = orders.filter(status=status)
    
    # Search by order number or customer
    search = request.GET.get('search', '')
    if search:
        orders = orders.filter(
            Q(order_number__icontains=search) |
            Q(user__name__icontains=search) |
            Q(user__email__icontains=search)
        )
    
    context = {
        'orders': orders,
        'status': status,
        'search': search,
        'status_choices': Order.STATUS_CHOICES,  # For filter dropdown
    }
    return render(request, 'admin/modules/orders/list.html', context)
```

### Order Detail

**Endpoint:** `/orders/{id}/`

```python
@user_passes_test(admin_required)
def order_detail(request, pk):
    """View order details"""
    order = get_object_or_404(
        Order.objects.select_related('user', 'shipping_address', 'billing_address').prefetch_related('items__variant__product'),
        pk=pk
    )
    
    context = {
        'order': order,
    }
    return render(request, 'admin/modules/orders/detail.html', context)
```

### Update Order Status

**Endpoint:** `/orders/{id}/status/`

```python
@user_passes_test(admin_required)
def order_status_update(request, pk):
    """Update order status"""
    order = get_object_or_404(Order, pk=pk)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
            messages.success(request, f'Order status updated to "{order.get_status_display()}"')
        else:
            messages.error(request, 'Invalid status')
    
    return redirect('dashboard:order_detail', pk=order.pk)
```

---

## Content Management

### Banner Management

**List Banners:** `/banners/`

**Add Banner:** `/banners/add/`

**Toggle Banner Status:** `/banners/{id}/toggle-status/`

```python
@user_passes_test(admin_required)
def banner_toggle_status(request, pk):
    """Toggle banner active status via AJAX"""
    banner = get_object_or_404(Banner, pk=pk)
    banner.is_active = not banner.is_active
    banner.save()
    
    return JsonResponse({
        'success': True,
        'is_active': banner.is_active
    })
```

---

## Template Structure

### Base Layout

**File:** `templates/admin/layouts/base.html`

```html
<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}BikeShop Admin{% endblock %}</title>
    <link rel="stylesheet" href="{% static 'assets/css/bootstrap.min.css' %}">
    <link rel="stylesheet" href="{% static 'assets/css/app.min.css' %}">
    {% block extra_css %}{% endblock %}
</head>
<body>
    <!-- Sidebar -->
    <div class="sidebar">
        {% include 'admin/layouts/sidebar.html' %}
    </div>
    
    <!-- Main Content -->
    <div class="main-content">
        <!-- Topbar -->
        <div class="topbar">
            {% include 'admin/layouts/topbar.html' %}
        </div>
        
        <!-- Page Content -->
        <div class="container-fluid">
            <!-- Flash Messages -->
            {% if messages %}
            <div class="messages">
                {% for message in messages %}
                <div class="alert alert-{{ message.tags }} alert-dismissible">
                    {{ message }}
                    <button type="button" class="close" data-dismiss="alert">&times;</button>
                </div>
                {% endfor %}
            </div>
            {% endif %}
            
            <!-- Page Content Block -->
            {% block content %}{% endblock %}
        </div>
    </div>
    
    <script src="{% static 'assets/js/jquery.min.js' %}"></script>
    <script src="{% static 'assets/js/bootstrap.bundle.min.js' %}"></script>
    {% block extra_js %}{% endblock %}
</body>
</html>
```

### Sidebar Navigation

**File:** `templates/admin/layouts/sidebar.html`

```html
<div class="sidebar-menu">
    <ul>
        <li>
            <a href="{% url 'dashboard:dashboard' %}">
                <i class="fas fa-home"></i>
                <span>Dashboard</span>
            </a>
        </li>
        <li>
            <a href="{% url 'dashboard:user_list' %}">
                <i class="fas fa-users"></i>
                <span>Users</span>
            </a>
        </li>
        <li class="submenu">
            <a href="#">
                <i class="fas fa-box"></i>
                <span>Catalog</span>
                <i class="fas fa-chevron-down"></i>
            </a>
            <ul class="submenu-items">
                <li><a href="{% url 'dashboard:product_list' %}">Products</a></li>
                <li><a href="{% url 'dashboard:category_list' %}">Categories</a></li>
                <li><a href="{% url 'dashboard:brand_list' %}">Brands</a></li>
                <li><a href="{% url 'dashboard:attribute_list' %}">Attributes</a></li>
            </ul>
        </li>
        <li>
            <a href="{% url 'dashboard:order_list' %}">
                <i class="fas fa-shopping-cart"></i>
                <span>Orders</span>
            </a>
        </li>
        <li>
            <a href="{% url 'dashboard:banner_list' %}">
                <i class="fas fa-image"></i>
                <span>Banners</span>
            </a>
        </li>
        <li>
            <a href="{% url 'dashboard:logout' %}">
                <i class="fas fa-sign-out-alt"></i>
                <span>Logout</span>
            </a>
        </li>
    </ul>
</div>
```

---

## URL Configuration

**File:** `apps/dashboard/urls.py`

```python
from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # Authentication
    path('login/', views.admin_login, name='login'),
    path('logout/', views.admin_logout, name='logout'),
    
    # Dashboard
    path('', views.admin_dashboard, name='dashboard'),
    
    # User Management
    path('users/', views.user_list, name='user_list'),
    path('users/add/', views.user_add, name='user_add'),
    path('users/<int:pk>/edit/', views.user_edit, name='user_edit'),
    path('users/<int:pk>/delete/', views.user_delete, name='user_delete'),
    
    # Categories
    path('categories/', views.category_list, name='category_list'),
    path('categories/add/', views.category_add, name='category_add'),
    path('categories/<int:pk>/edit/', views.category_edit, name='category_edit'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),
    
    # Brands
    path('brands/', views.brand_list, name='brand_list'),
    path('brands/add/', views.brand_add, name='brand_add'),
    path('brands/<int:pk>/edit/', views.brand_edit, name='brand_edit'),
    path('brands/<int:pk>/delete/', views.brand_delete, name='brand_delete'),
    
    # Products
    path('products/', views.product_list, name='product_list'),
    path('products/add/', views.product_add, name='product_add'),
    path('products/<int:pk>/edit/', views.product_edit, name='product_edit'),
    path('products/<int:pk>/delete/', views.product_delete, name='product_delete'),
    
    # Product Variants
    path('products/<int:product_id>/variants/', views.variant_list, name='variant_list'),
    path('products/<int:product_id>/variants/add/', views.variant_add, name='variant_add'),
    path('variants/<int:pk>/edit/', views.variant_edit, name='variant_edit'),
    path('variants/<int:pk>/delete/', views.variant_delete, name='variant_delete'),
    
    # Attributes
    path('attributes/', views.attribute_list, name='attribute_list'),
    path('attributes/add/', views.attribute_add, name='attribute_add'),
    path('attributes/<int:pk>/edit/', views.attribute_edit, name='attribute_edit'),
    path('attributes/<int:pk>/delete/', views.attribute_delete, name='attribute_delete'),
    
    # Orders
    path('orders/', views.order_list, name='order_list'),
    path('orders/<int:pk>/', views.order_detail, name='order_detail'),
    path('orders/<int:pk>/status/', views.order_status_update, name='order_status_update'),
    
    # Banners
    path('banners/', views.banner_list, name='banner_list'),
    path('banners/add/', views.banner_add, name='banner_add'),
    path('banners/<int:pk>/edit/', views.banner_edit, name='banner_edit'),
    path('banners/<int:pk>/delete/', views.banner_delete, name='banner_delete'),
    path('banners/<int:pk>/toggle-status/', views.banner_toggle_status, name='banner_toggle_status'),
]
```

**Main URL Configuration:** `bike_shop/urls.py`

```python
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),  # Django default admin
    path('api/', include('api.urls')),  # REST API
    path('', include('dashboard.urls')),  # Custom admin dashboard (root)
]
```

---

## Security & Permissions

### Access Control Layers

```
1. Authentication Check
   ↓ (Is user logged in?)
2. Staff Check
   ↓ (Is user.is_staff = True?)
3. View Permission
   ↓ (Can perform this action?)
4. Object Permission
   ↓ (Can access this specific object?)
```

### Best Practices

1. **Always Use Decorators:**
   ```python
   @user_passes_test(admin_required)
   def protected_view(request):
       pass
   ```

2. **Validate User Input:**
   ```python
   if not email or not name:
       messages.error(request, 'Required fields missing')
       return
   ```

3. **Prevent Self-Deletion:**
   ```python
   if user_obj == request.user:
       messages.error(request, 'Cannot delete yourself')
       return
   ```

4. **Use CSRF Tokens:**
   ```html
   <form method="POST">
       {% csrf_token %}
       ...
   </form>
   ```

5. **Confirm Destructive Actions:**
   ```python
   if request.method == 'POST':
       # Only delete on POST confirmation
       obj.delete()
   ```

---

## Summary

### Key Features

- ✅ Custom-built admin interface
- ✅ Staff-only access with security checks
- ✅ Complete CRUD operations for all models
- ✅ Search and filter functionality
- ✅ Real-time analytics dashboard
- ✅ Stock management and alerts
- ✅ Order processing
- ✅ Content management (banners, featured sections)

### Access Management

| Feature | Endpoint | Permission Required |
|---------|----------|---------------------|
| Login | `/login/` | None |
| Dashboard | `/` | Staff only |
| User Management | `/users/` | Staff only |
| Catalog Management | `/products/`, `/categories/`, `/brands/` | Staff only |
| Order Management | `/orders/` | Staff only |

---

**Next:** [09_PACKAGES_EXPLAINED.md](./09_PACKAGES_EXPLAINED.md) - Package Documentation

**Previous:** [07_API_ENDPOINTS.md](./07_API_ENDPOINTS.md) - API Endpoints Reference
