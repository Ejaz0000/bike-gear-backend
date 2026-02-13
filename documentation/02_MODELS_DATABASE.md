# Database Models - Complete Explanation

**Part 3 of Complete Documentation Series**

---

## 📋 Table of Contents

1. [Database Schema Overview](#database-schema-overview)
2. [Accounts App Models](#accounts-app-models)
3. [Catalog App Models](#catalog-app-models)
4. [Cart App Models](#cart-app-models)
5. [Core App Models](#core-app-models)
6. [Model Relationships](#model-relationships)
7. [Common Patterns](#common-patterns)

---

## 1. Database Schema Overview

### Entity Relationship Diagram

```
┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│     User     │────────▶│   Address    │         │   Category   │
│              │ 1     * │              │         │              │
│ - id         │         │ - id         │         │ - id         │
│ - email      │         │ - street     │         │ - name       │
│ - name       │         │ - city       │         │ - slug       │
│ - phone      │         │ - is_default │         │ - parent  ◀──┐self
└──────┬───────┘         └──────────────┘         └──────┬───────┘
       │ 1                                                │ 1
       │                                                  │
       │ *                                                │ *
┌──────▼───────┐         ┌──────────────┐         ┌──────▼───────┐
│     Cart     │────────▶│  CartItem    │◀────────│   Product    │
│              │ 1     * │              │ *     1 │              │
│ - user_id    │         │ - variant_id │         │ - title      │
│ - session_key│         │ - quantity   │         │ - price      │
└──────────────┘         │ - price_snap │         │ - stock      │
                         └──────┬───────┘         └──────┬───────┘
                                │ *                      │ 1
                                │                        │
                                │ 1                      │ *
                         ┌──────▼────────┐        ┌──────▼───────┐
                         │ ProductVariant│        │ProductImage  │
                         │               │        │              │
                         │ - sku         │        │ - image      │
                         │ - price       │        │ - position   │
                         │ - stock       │        └──────────────┘
                         └──────┬────────┘
                                │ *
                                │
                                │ *
                         ┌──────▼────────┐
                         │VariantAttr    │
                         │               │
                         │ - attr_value  │
                         └───────────────┘
```

### Database Tables

**Accounts:**
- `users` - Custom user model
- `addresses` - User shipping/billing addresses
- `password_reset_tokens` - Password reset functionality

**Catalog:**
- `categories` - Product categories (hierarchical)
- `brands` - Product brands
- `products` - Main products table
- `product_variants` - Product variations (size/color)
- `product_images` - Product images
- `attribute_types` - Attribute definitions (Color, Size)
- `attribute_values` - Attribute options (Red, Large)
- `variant_attributes` - Link variants to attributes

**Cart:**
- `carts` - Shopping carts
- `cart_items` - Items in cart

**Core:**
- `banners` - Homepage banners
- `featured_sections` - Featured product sections

---

## 2. Accounts App Models

### User Model

**File:** `apps/accounts/models.py`

```python
class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']
```

#### Line-by-Line Explanation

**Inheritance:**
```python
class User(AbstractBaseUser, PermissionsMixin):
```
- `AbstractBaseUser` - Provides core user authentication
  - password hashing
  - login/logout functionality
  - last_login tracking
- `PermissionsMixin` - Adds permissions and groups
  - is_superuser field
  - groups relationship
  - user_permissions relationship

**Why custom user?** Default Django user uses username. We need email-based authentication.

**Fields:**

1. **Email Field**
```python
email = models.EmailField(max_length=255, unique=True)
```
- Type: `EmailField` (validates email format)
- `max_length=255` - Maximum characters allowed
- `unique=True` - No two users can have same email
- **Database:** Creates UNIQUE constraint
- **Django:** Validates format (user@example.com)

2. **Name Field**
```python
name = models.CharField(max_length=255)
```
- Type: `CharField` - Regular text field
- Stores full name (not split into first/last)
- **Why?** Simpler for international names

3. **Phone Field**
```python
phone = models.CharField(max_length=20, blank=True, null=True)
```
- `blank=True` - Form validation allows empty
- `null=True` - Database allows NULL
- **Both needed:** Django forms + Database
- **Why CharField not PhoneField?** More flexible for international formats

4. **Active Status**
```python
is_active = models.BooleanField(default=True)
```
- Controls if user can login
- `default=True` - New users active by default
- **Use case:** Soft delete (mark inactive instead of deleting)

5. **Staff Status**
```python
is_staff = models.BooleanField(default=False)
```
- Controls Django admin access
- `default=False` - Regular users can't access admin
- **True:** Can access admin panel

6. **Date Joined**
```python
date_joined = models.DateTimeField(auto_now_add=True)
```
- `auto_now_add=True` - Set once when created
- Never updates after creation
- Useful for user analytics

**Custom Manager:**
```python
objects = UserManager()
```
- Replaces default manager
- Provides custom `create_user()` and `create_superuser()` methods

**Authentication Configuration:**
```python
USERNAME_FIELD = 'email'
REQUIRED_FIELDS = ['name']
```
- `USERNAME_FIELD` - Field used for login (email instead of username)
- `REQUIRED_FIELDS` - Required when creating superuser (excluding email and password)

### UserManager

```python
class UserManager(BaseUserManager):

    def create_user(self, email, name, password=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        
        if not name:
            raise ValueError('Users must have a name')
        
        email = self.normalize_email(email)  # Convert to lowercase

        user = self.model(
            email=email,
            name=name,
            **extra_fields
        )

        user.set_password(password)  # Hash password
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, name, password, **extra_fields)
```

#### Key Points

1. **`normalize_email(email)`**
   - Converts domain to lowercase
   - `User@EXAMPLE.COM` → `User@example.com`
   - Prevents duplicate emails with different cases

2. **`set_password(password)`**
   - NEVER store plain password
   - Uses PBKDF2 algorithm with SHA256 hash
   - Adds salt automatically
   - **Security:** Cannot reverse to get original password

3. **`create_superuser` defaults**
   - `is_staff=True` - Can access admin
   - `is_superuser=True` - Has all permissions
   - `is_active=True` - Can login immediately

### Address Model

```python
class Address(models.Model):

    ADDRESS_TYPE_CHOICES = [
        ('billing', 'Billing'),
        ('shipping', 'Shipping'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='addresses'
    )

    label = models.CharField(max_length=50)
    address_type = models.CharField(
        max_length=20,
        choices=ADDRESS_TYPE_CHOICES,
        default='shipping'
    )

    street = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default='Bangladesh')
    phone = models.CharField(max_length=20)

    is_default_billing = models.BooleanField(default=False)
    is_default_shipping = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

#### Important Concepts

**ForeignKey Relationship:**
```python
user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
```
- **ForeignKey:** Many addresses → One user
- **on_delete=CASCADE:** Delete addresses when user is deleted
- **related_name='addresses':** Access via `user.addresses.all()`

**Choices Field:**
```python
address_type = models.CharField(choices=ADDRESS_TYPE_CHOICES)
```
- Restricts values to defined choices
- Database stores 'billing' or 'shipping'
- Forms show "Billing" or "Shipping"

**Unique Constraint:**
```python
class Meta:
    constraints = [
        models.UniqueConstraint(
            fields=['user', 'address_type', 'is_default_billing'],
            condition=models.Q(is_default_billing=True),
            name='unique_default_billing_per_user'
        ),
    ]
```
- **Purpose:** Only ONE default billing address per user
- **Condition:** Only applies when `is_default_billing=True`
- **Result:** User can't have multiple default addresses

**Custom Save Method:**
```python
def save(self, *args, **kwargs):
    if self.is_default_billing:
        # Unset other default billing addresses
        Address.objects.filter(
            user=self.user,
            address_type='billing',
            is_default_billing=True
        ).exclude(pk=self.pk).update(is_default_billing=False)
    
    super().save(*args, **kwargs)
```
- **Logic:** When setting address as default, unset all others
- `.exclude(pk=self.pk)` - Don't update self
- `.update(is_default_billing=False)` - Bulk update

---

## 3. Catalog App Models

### Category Model

```python
class Category(models.Model):
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True, db_index=True)
    
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children'
    )
    
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    display_order = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

#### Key Concepts

**Self-Referencing ForeignKey:**
```python
parent = models.ForeignKey('self', ...)
```
- **'self'** - References same model
- **Purpose:** Hierarchical categories
- **Example:**
  ```
  Bikes (parent=NULL)
    ├─ Mountain Bikes (parent=Bikes)
    ├─ Road Bikes (parent=Bikes)
    └─ Electric Bikes (parent=Bikes)
  ```

**Slug Field:**
```python
slug = models.SlugField(max_length=200, unique=True, db_index=True)
```
- **URL-friendly:** "Mountain Bikes" → "mountain-bikes"
- **db_index=True:** Database index for fast lookups
- **Used in URLs:** `/categories/mountain-bikes/`

**Auto-Generate Slug:**
```python
def save(self, *args, **kwargs):
    if not self.slug:
        self.slug = slugify(self.name)
    super().save(*args, **kwargs)
```
- `slugify()` - Django utility function
- Only generates if slug is empty
- **Example:** "Men's Helmets" → "mens-helmets"

### Product Model

```python
class Product(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=255, unique=True, db_index=True)
    
    brand = models.ForeignKey(
        Brand,
        on_delete=models.SET_NULL,
        related_name='products',
        null=True,
        blank=True
    )
    
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='products',
        null=True,
        blank=True
    )
    
    description = models.TextField(blank=True)
    
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    
    sale_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        blank=True,
        null=True
    )
    
    stock = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.CharField(max_length=300, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

#### Important Features

**on_delete=SET_NULL:**
```python
brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True)
```
- **When brand deleted:** Product.brand becomes NULL
- **Why not CASCADE?** Don't delete products when brand deleted
- **Requires:** `null=True`

**DecimalField for Money:**
```python
price = models.DecimalField(max_digits=10, decimal_places=2)
```
- **max_digits=10:** Total digits (including decimals)
- **decimal_places=2:** Digits after decimal
- **Example:** 99999999.99 (max value)
- **Why not FloatField?** Decimal is precise (no rounding errors)

**Validators:**
```python
validators=[MinValueValidator(0)]
```
- **Database level:** Ensures price >= 0
- **Form level:** Shows error if negative price entered
- **Built-in validator:** Django provides many

**Custom Methods:**
```python
def get_total_stock(self):
    """Calculate total stock across all variants."""
    total = self.variants.filter(is_active=True).aggregate(
        total_stock=models.Sum('stock')
    )['total_stock']
    return total if total else 0
```
- **aggregate():** Database aggregation function
- **Sum('stock'):** Add up all variant stocks
- Returns 0 if no variants

**Meta Class:**
```python
class Meta:
    db_table = 'products'
    ordering = ['-created_at']
    indexes = [
        models.Index(fields=['slug']),
        models.Index(fields=['is_active', '-created_at']),
    ]
```
- **db_table:** Custom table name (default: catalog_product)
- **ordering:** Default sort order (newest first)
- **indexes:** Database indexes for performance

### Product Variant System

The variant system allows products to have multiple options (size, color, etc.)

```python
class AttributeType(models.Model):
    """E.g., Color, Size, Material"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    display_order = models.IntegerField(default=0)

class AttributeValue(models.Model):
    """E.g., Red, Blue, Large, Small"""
    attribute_type = models.ForeignKey(AttributeType, on_delete=models.CASCADE)
    value = models.CharField(max_length=200)
    
    class Meta:
        unique_together = ['attribute_type', 'value']

class ProductVariant(models.Model):
    """Specific combination: Red + Large"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    sku = models.CharField(max_length=100, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    stock = models.PositiveIntegerField(default=0)

class VariantAttribute(models.Model):
    """Junction table linking variant to attributes"""
    product_variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
    attribute_value = models.ForeignKey(AttributeValue, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ['product_variant', 'attribute_value']
```

#### How It Works

**Example: T-Shirt Product**

1. **Create Attribute Types:**
   ```
   AttributeType: Color
   AttributeType: Size
   ```

2. **Create Attribute Values:**
   ```
   Color: Red, Blue, Green
   Size: Small, Medium, Large
   ```

3. **Create Product:**
   ```
   Product: "Basic T-Shirt"
   Price: $20 (base price)
   ```

4. **Create Variants:**
   ```
   Variant 1: Red + Small  (SKU: TSHIRT-RED-S, Price: $20, Stock: 10)
   Variant 2: Red + Medium (SKU: TSHIRT-RED-M, Price: $20, Stock: 15)
   Variant 3: Blue + Small (SKU: TSHIRT-BLU-S, Price: $22, Stock: 8)
   ```

5. **Link Attributes via VariantAttribute:**
   ```
   VariantAttribute: Variant1 → Color:Red
   VariantAttribute: Variant1 → Size:Small
   VariantAttribute: Variant2 → Color:Red
   VariantAttribute: Variant2 → Size:Medium
   ```

---

## 4. Cart App Models

### Cart Model

```python
class Cart(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='carts'
    )
    
    session_key = models.CharField(
        max_length=40,
        null=True,
        blank=True,
        db_index=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

#### Key Design Decisions

**Optional User:**
```python
user = models.ForeignKey(..., null=True, blank=True)
```
- **Why?** Support guest (anonymous) carts
- **Guest cart:** user=NULL, session_key="abc123"
- **User cart:** user=User object, session_key=NULL

**Session Key:**
```python
session_key = models.CharField(max_length=40, db_index=True)
```
- **Purpose:** Link cart to browser session
- **Django sessions:** Automatically generated unique key
- **db_index=True:** Fast lookups by session

**Helper Methods:**
```python
def get_total_items(self):
    return sum(item.quantity for item in self.items.all())

def get_subtotal(self):
    return sum(item.get_total() for item in self.items.all())
```
- **No database fields:** Calculated on-the-fly
- **Why?** Always accurate, no sync issues

### CartItem Model

```python
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)]
    )
    
    price_snapshot = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

#### Important Features

**Price Snapshot:**
```python
price_snapshot = models.DecimalField(...)
```
- **Purpose:** Preserve price when added to cart
- **Why?** Product price might change later
- **Customer protection:** Pay the price shown when added

**Constraints:**
```python
class Meta:
    constraints = [
        models.CheckConstraint(
            check=(
                models.Q(variant__isnull=False, product__isnull=True) |
                models.Q(variant__isnull=True, product__isnull=False)
            ),
            name='cart_item_variant_or_product'
        ),
    ]
```
- **Rule:** Either variant OR product (not both)
- **Database enforced:** Cannot violate this rule

---

## 5. Common Patterns

### auto_now vs auto_now_add

```python
created_at = models.DateTimeField(auto_now_add=True)  # Set once on creation
updated_at = models.DateTimeField(auto_now=True)      # Update on every save
```

### null vs blank

```python
phone = models.CharField(blank=True, null=True)
```
- **blank=True:** Form validation (optional in forms)
- **null=True:** Database level (allows NULL in database)
- **Both usually needed together**

### related_name

```python
user = models.ForeignKey(User, related_name='addresses')
```
- **Usage:** `user.addresses.all()` instead of `user.address_set.all()`
- **More readable code**

---

**Continue to `03_API_ARCHITECTURE.md` for REST API implementation details.**
