# Shopping Cart System - Complete Guide

**Part 5 of Complete Documentation Series**

---

## 📋 Table of Contents

1. [Cart Architecture](#cart-architecture)
2. [Guest vs Authenticated Carts](#guest-vs-authenticated-carts)
3. [Cart Models Explained](#cart-models-explained)
4. [Cart Operations](#cart-operations)
5. [Session Management](#session-management)
6. [Cart Merging on Login](#cart-merging-on-login)
7. [Price Snapshot Feature](#price-snapshot-feature)
8. [Stock Validation](#stock-validation)

---

## 1. Cart Architecture

### Design Goals

Our cart system needs to support:
- ✅ **Guest users** - Shop without account
- ✅ **Authenticated users** - Persistent cart
- ✅ **Cart merging** - Merge guest cart when user logs in
- ✅ **Price protection** - Store price at time of adding
- ✅ **Stock validation** - Prevent overselling
- ✅ **Product variants** - Support different sizes/colors

### System Overview

```
┌──────────────────────────────────────────────────────────┐
│                    CART SYSTEM                            │
└──────────────────────────────────────────────────────────┘
                           │
          ┌────────────────┴────────────────┐
          │                                  │
          ▼                                  ▼
┌─────────────────────┐          ┌─────────────────────┐
│    GUEST CART       │          │   USER CART         │
│  (Session-Based)    │          │  (Database-Based)   │
├─────────────────────┤          ├─────────────────────┤
│ user: NULL          │          │ user: User object   │
│ session_key: "abc"  │          │ session_key: NULL   │
└─────────────────────┘          └─────────────────────┘
          │                                  │
          └────────────────┬─────────────────┘
                           │
                           ▼
                   ┌───────────────┐
                   │   CART ITEMS  │
                   ├───────────────┤
                   │ - variant     │
                   │ - quantity    │
                   │ - price_snap  │
                   └───────────────┘
```

---

## 2. Guest vs Authenticated Carts

### Guest Cart Flow

```
┌─────────────────────────────────────────────────────────────┐
│                   1. USER VISITS SITE                        │
│                   (No login required)                        │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│           2. DJANGO CREATES SESSION                          │
│   - Generates unique session key: "x7f3k9m2..."             │
│   - Stores in cookie                                         │
│   - Creates session in database                              │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│               3. USER ADDS ITEM TO CART                      │
│   POST /api/cart/items/                                      │
│   { "variant_id": 1, "quantity": 2 }                        │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              4. SERVER CREATES GUEST CART                    │
│   Cart.objects.create(                                       │
│       user=None,                                             │
│       session_key=request.session.session_key                │
│   )                                                          │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              5. ADD ITEM TO CART                             │
│   CartItem.objects.create(                                   │
│       cart=guest_cart,                                       │
│       variant=variant,                                       │
│       quantity=2,                                            │
│       price_snapshot=variant.price                           │
│   )                                                          │
└─────────────────────────────────────────────────────────────┘
```

### Authenticated Cart Flow

```
┌─────────────────────────────────────────────────────────────┐
│                   1. USER LOGS IN                            │
│   POST /api/auth/login/                                      │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              2. SERVER CHECKS FOR EXISTING CARTS             │
│   - Guest cart (session_key)                                 │
│   - User cart (user_id)                                      │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                 3. MERGE CARTS IF BOTH EXIST                 │
│   (See Cart Merging section)                                 │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│           4. SUBSEQUENT REQUESTS USE USER CART               │
│   cart = Cart.objects.get(user=request.user)                │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Cart Models Explained

### Cart Model

**File:** `apps/cart/models.py`

```python
class Cart(models.Model):
    """
    Shopping cart - can belong to user or be anonymous (session-based)
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='carts',
        help_text='Cart owner (null for guest carts)'
    )
    
    session_key = models.CharField(
        max_length=40,
        null=True,
        blank=True,
        db_index=True,
        help_text='Session ID for anonymous users'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def get_total_items(self):
        """Get total number of items in cart"""
        return sum(item.quantity for item in self.items.all())
    
    def get_subtotal(self):
        """Calculate cart subtotal (before shipping/tax)"""
        return sum(item.get_total() for item in self.items.all())
    
    def get_total_savings(self):
        """Calculate total savings from discounts"""
        return sum(item.get_savings() for item in self.items.all())
```

### Field Analysis

**1. User Field (Nullable)**
```python
user = models.ForeignKey(..., null=True, blank=True)
```
- **Purpose:** Link cart to authenticated user
- **null=True:** Allows guest carts (user=None)
- **blank=True:** Form validation allows empty
- **on_delete=CASCADE:** Delete cart when user deleted

**2. Session Key (Nullable)**
```python
session_key = models.CharField(max_length=40, null=True, blank=True, db_index=True)
```
- **Purpose:** Link cart to browser session
- **max_length=40:** Django session key length
- **db_index=True:** Fast lookups by session
- **Example:** `"x7f3k9m2p5q8r1s4t6u9v2w5x8y1z4a7"`

**Cart Types:**
```python
# Guest cart
cart = Cart(user=None, session_key="x7f3k9m2...")

# User cart
cart = Cart(user=user_obj, session_key=None)
```

### CartItem Model

```python
class CartItem(models.Model):
    """Individual items in cart"""
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items'
    )
    
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cart_items'
    )
    
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cart_items'
    )
    
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)]
    )
    
    price_snapshot = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text='Price when added to cart'
    )
    
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### Key Decisions

**1. Why both variant and product?**
```python
variant = models.ForeignKey(ProductVariant, null=True)
product = models.ForeignKey(Product, null=True)
```
- **Products WITH variants:** Use variant field
- **Products WITHOUT variants:** Use product field directly
- **Constraint:** Must have one (not both)

**2. Price Snapshot**
```python
price_snapshot = models.DecimalField(...)
```
- **Purpose:** Preserve price at time of adding
- **Why?** Product price might change later
- **Customer protection:** Pay what they saw

**Example:**
```
Day 1: Product price = $100, user adds to cart
Day 2: Admin raises price to $120
Day 3: User checks out
Result: User pays $100 (price_snapshot)
```

### Model Methods

```python
def get_total(self):
    """Total price for this cart item"""
    return self.quantity * self.price_snapshot

def get_savings(self):
    """Savings if on sale"""
    if self.variant:
        regular_price = self.variant.price
    else:
        regular_price = self.product.price
    
    if self.price_snapshot < regular_price:
        return (regular_price - self.price_snapshot) * self.quantity
    return 0

def is_available(self):
    """Check if product is still available"""
    if self.variant:
        return self.variant.is_active and self.variant.stock >= self.quantity
    return self.product.is_active and self.product.stock >= self.quantity
```

---

## 4. Cart Operations

### Get or Create Cart

**File:** `apps/api/views/cart.py`

```python
def get_or_create_cart(request):
    """Get existing cart or create new one"""
    
    # If user is authenticated
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(
            user=request.user,
            defaults={'session_key': None}
        )
        return cart
    
    # If guest user
    # Ensure session exists
    if not request.session.session_key:
        request.session.create()
    
    session_key = request.session.session_key
    cart, created = Cart.objects.get_or_create(
        session_key=session_key,
        user=None,
        defaults={}
    )
    return cart
```

### Add to Cart

```python
class AddToCartView(APIView):
    """POST /api/cart/items/ - Add item to cart"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = AddToCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Get or create cart
        cart = get_or_create_cart(request)
        
        variant_id = serializer.validated_data['variant_id']
        quantity = serializer.validated_data['quantity']
        
        # Get variant
        try:
            variant = ProductVariant.objects.get(id=variant_id)
        except ProductVariant.DoesNotExist:
            return Response(
                {'error': 'Product variant not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check stock
        if variant.stock < quantity:
            return Response(
                {'error': f'Only {variant.stock} items available'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if item already in cart
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            variant=variant,
            defaults={
                'quantity': quantity,
                'price_snapshot': variant.get_effective_price()
            }
        )
        
        # If already exists, update quantity
        if not created:
            cart_item.quantity += quantity
            
            # Check stock again
            if variant.stock < cart_item.quantity:
                return Response(
                    {'error': f'Only {variant.stock} items available'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            cart_item.save()
        
        return Response(
            CartItemSerializer(cart_item).data,
            status=status.HTTP_201_CREATED
        )
```

### Update Quantity

```python
class UpdateCartItemView(APIView):
    """PATCH /api/cart/items/{id}/ - Update item quantity"""
    permission_classes = [AllowAny]
    
    def patch(self, request, pk):
        cart = get_or_create_cart(request)
        
        try:
            cart_item = CartItem.objects.get(id=pk, cart=cart)
        except CartItem.DoesNotExist:
            return Response(
                {'error': 'Cart item not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = UpdateCartItemSerializer(
            cart_item,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        
        # Validate stock
        new_quantity = serializer.validated_data.get('quantity')
        if new_quantity:
            if cart_item.variant.stock < new_quantity:
                return Response(
                    {'error': f'Only {cart_item.variant.stock} items available'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        serializer.save()
        return Response(serializer.data)
```

### Remove from Cart

```python
class RemoveCartItemView(APIView):
    """DELETE /api/cart/items/{id}/ - Remove item from cart"""
    permission_classes = [AllowAny]
    
    def delete(self, request, pk):
        cart = get_or_create_cart(request)
        
        try:
            cart_item = CartItem.objects.get(id=pk, cart=cart)
            cart_item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except CartItem.DoesNotExist:
            return Response(
                {'error': 'Cart item not found'},
                status=status.HTTP_404_NOT_FOUND
            )
```

---

## 5. Session Management

### How Django Sessions Work

**Session Creation:**
```python
# Automatic on first request
request.session  # Creates session if doesn't exist
request.session.session_key  # Unique identifier
```

**Session Cookie:**
```
Set-Cookie: sessionid=x7f3k9m2p5q8r1s4t6u9v2w5x8y1z4a7; Path=/; HttpOnly
```

**Session Storage:**
```python
# settings.py
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
```

**Database Table:**
```
django_session
  - session_key (PK): "x7f3k9m2..."
  - session_data: encrypted data
  - expire_date: expiration timestamp
```

### Session Configuration

```python
# settings.py
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_NAME = 'sessionid'
SESSION_COOKIE_AGE = 1209600  # 2 weeks
SESSION_SAVE_EVERY_REQUEST = True
SESSION_COOKIE_HTTPONLY = False  # For JavaScript access (dev only)
SESSION_COOKIE_SECURE = False    # Set True in production (HTTPS)
SESSION_COOKIE_SAMESITE = 'Lax'
```

### Ensuring Session Exists

```python
def get_or_create_cart(request):
    # Ensure session exists for guest users
    if not request.session.session_key:
        request.session.create()
    
    session_key = request.session.session_key
    # Now can use session_key to find cart
```

---

## 6. Cart Merging on Login

### Why Merge?

**Scenario:**
1. Guest adds items to cart
2. Guest logs in
3. User already has saved cart from previous session
4. **Question:** What happens to both carts?

**Answer:** Merge them!

### Merge Logic

```python
def merge_carts(guest_cart, user_cart):
    """
    Merge guest cart into user cart
    """
    if not guest_cart:
        return user_cart
    
    # Get all items from guest cart
    guest_items = guest_cart.items.all()
    
    for guest_item in guest_items:
        # Check if user cart already has this variant
        user_item = user_cart.items.filter(
            variant=guest_item.variant
        ).first()
        
        if user_item:
            # Add quantities together
            user_item.quantity += guest_item.quantity
            
            # Update price if guest price is lower (better deal)
            if guest_item.price_snapshot < user_item.price_snapshot:
                user_item.price_snapshot = guest_item.price_snapshot
            
            user_item.save()
        else:
            # Move item to user cart
            guest_item.cart = user_cart
            guest_item.save()
    
    # Delete guest cart
    guest_cart.delete()
    
    return user_cart
```

### When Merging Happens

```python
class LoginView(APIView):
    def post(self, request):
        # ... authentication ...
        
        # After successful login
        user = authenticated_user
        
        # Get guest cart (if exists)
        guest_cart = None
        if request.session.session_key:
            guest_cart = Cart.objects.filter(
                session_key=request.session.session_key,
                user=None
            ).first()
        
        # Get or create user cart
        user_cart, created = Cart.objects.get_or_create(user=user)
        
        # Merge if guest cart exists
        if guest_cart:
            user_cart = merge_carts(guest_cart, user_cart)
        
        # Return response with token
        # ...
```

---

## 7. Price Snapshot Feature

### Why Price Snapshot?

**Problem:**
- Product added to cart at $100
- Admin changes price to $120
- Customer expects to pay $100

**Solution:** Store price at time of adding

### Implementation

```python
class CartItem(models.Model):
    price_snapshot = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text='Price when added to cart'
    )
```

**Setting snapshot:**
```python
CartItem.objects.create(
    cart=cart,
    variant=variant,
    quantity=quantity,
    price_snapshot=variant.get_effective_price()  # Current price
)
```

**get_effective_price():**
```python
# ProductVariant model
def get_effective_price(self):
    """Return sale price if available, otherwise regular price"""
    if self.sale_price and self.sale_price < self.price:
        return self.sale_price
    return self.price
```

### Calculating Total

```python
def get_total(self):
    """Use snapshot price, not current price"""
    return self.quantity * self.price_snapshot  # Not variant.price!
```

---

## 8. Stock Validation

### Validation Points

**1. When Adding to Cart:**
```python
if variant.stock < quantity:
    raise ValidationError('Insufficient stock')
```

**2. When Updating Quantity:**
```python
if variant.stock < new_quantity:
    raise ValidationError('Insufficient stock')
```

**3. During Checkout:**
```python
for item in cart.items.all():
    if not item.is_available():
        raise ValidationError(f'{item.product.title} is out of stock')
```

### Real-Time Stock Check

```python
def is_available(self):
    """Check if item can still be purchased"""
    if self.variant:
        return (
            self.variant.is_active and
            self.variant.stock >= self.quantity
        )
    return (
        self.product.is_active and
        self.product.stock >= self.quantity
    )
```

---

**Continue to `06_CATALOG_PRODUCTS.md` for product management details.**
