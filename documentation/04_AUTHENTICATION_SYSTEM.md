# Authentication System - Complete Guide

**Part 4 of Complete Documentation Series**

---

## 📋 Table of Contents

1. [Custom User Model](#custom-user-model)
2. [JWT Authentication Flow](#jwt-authentication-flow)
3. [Registration Process](#registration-process)
4. [Login Process](#login-process)
5. [Protected Routes](#protected-routes)
6. [Password Management](#password-management)
7. [Address Management](#address-management)
8. [Security Best Practices](#security-best-practices)

---

## 1. Custom User Model

### Why Custom User Model?

Django's default User model uses `username` for authentication. We need:
- ✅ Email-based authentication
- ✅ Phone number field
- ✅ Simpler structure (no unnecessary fields)

### User Model Structure

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

### Field Explanations

**1. email (Username)**
```python
email = models.EmailField(max_length=255, unique=True)
```
- **Purpose:** User's unique identifier for login
- **Validation:** Automatically validates email format
- **Unique:** No two users can have same email
- **Database:** Creates unique index for fast lookups

**2. name (Full Name)**
```python
name = models.CharField(max_length=255)
```
- **Purpose:** User's display name
- **Why not first_name/last_name?** Simpler, international-friendly
- **Required:** Must be provided during registration

**3. phone (Optional Contact)**
```python
phone = models.CharField(max_length=20, blank=True, null=True)
```
- **Purpose:** Contact number for orders/support
- **Optional:** Can be added later
- **CharField:** Supports international formats (+880...)

**4. is_active (Account Status)**
```python
is_active = models.BooleanField(default=True)
```
- **Purpose:** Enable/disable account without deletion
- **True:** User can login
- **False:** User cannot login (soft delete)
- **Use cases:** Ban user, email verification pending

**5. is_staff (Admin Access)**
```python
is_staff = models.BooleanField(default=False)
```
- **Purpose:** Django admin panel access
- **True:** Can access `/admin/` interface
- **False:** Regular user (no admin access)
- **Superuser:** `is_staff=True` + `is_superuser=True`

**6. date_joined (Registration Date)**
```python
date_joined = models.DateTimeField(auto_now_add=True)
```
- **Purpose:** Track when user registered
- **auto_now_add=True:** Set once on creation
- **Never changes:** Even if user updates profile

### UserManager

```python
class UserManager(BaseUserManager):
    def create_user(self, email, name, password=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        
        if not name:
            raise ValueError('Users must have a name')
        
        # Normalize email (lowercase domain)
        email = self.normalize_email(email)

        user = self.model(
            email=email,
            name=name,
            **extra_fields
        )

        user.set_password(password)  # Hash password
        user.save(using=self._db)
        return user
```

**Key Methods:**

1. **normalize_email()**
   ```python
   email = self.normalize_email(email)
   # "User@EXAMPLE.com" → "User@example.com"
   ```
   - Converts domain to lowercase
   - Prevents duplicate emails with different cases

2. **set_password()**
   ```python
   user.set_password(password)
   ```
   - **Never stores plain password**
   - Uses PBKDF2 with SHA256 hash
   - Automatically adds salt
   - Result: `pbkdf2_sha256$260000$...`

---

## 2. JWT Authentication Flow

### What is JWT?

**JWT** = JSON Web Token (Pronounced "jot")

**Structure:**
```
eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoxfQ.signature
│              HEADER             │      PAYLOAD     │ SIGNATURE
```

**Decoded:**
```json
// Header
{
  "typ": "JWT",
  "alg": "HS256"
}

// Payload
{
  "user_id": 1,
  "email": "user@example.com",
  "exp": 1732456789,  // Expiration timestamp
  "iat": 1731852789   // Issued at timestamp
}

// Signature (prevents tampering)
HMACSHA256(
  base64UrlEncode(header) + "." + base64UrlEncode(payload),
  SECRET_KEY
)
```

### Complete Authentication Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    1. USER REGISTRATION                      │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  POST /api/auth/register/                                    │
│  {                                                            │
│    "email": "user@example.com",                              │
│    "name": "John Doe",                                       │
│    "password": "securepass123"                               │
│  }                                                            │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  Server:                                                      │
│  1. Validate email doesn't exist                             │
│  2. Hash password                                            │
│  3. Create user in database                                  │
│  4. Generate JWT token                                       │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  Response:                                                    │
│  {                                                            │
│    "user": {"id": 1, "email": "...", "name": "..."},        │
│    "token": "eyJ0eXAiOiJKV1QiLCJ..."                         │
│  }                                                            │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    2. CLIENT STORES TOKEN                    │
│  localStorage.setItem('token', token)                        │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              3. AUTHENTICATED API REQUEST                    │
│  GET /api/auth/profile/                                      │
│  Headers:                                                    │
│    Authorization: Bearer eyJ0eXAiOiJKV1QiLCJ...             │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  Server (Middleware):                                        │
│  1. Extract token from header                                │
│  2. Decode and verify signature                              │
│  3. Check expiration                                         │
│  4. Load user from database                                  │
│  5. Set request.user = User object                           │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  View executes with authenticated user                       │
│  return Response(UserSerializer(request.user).data)          │
└─────────────────────────────────────────────────────────────┘
```

### Token Generation

**File:** `apps/api/serializers/auth.py`

```python
def generate_jwt_token(user):
    """Generate JWT access token for user"""
    from rest_framework_simplejwt.tokens import AccessToken
    
    token = AccessToken.for_user(user)
    return str(token)
```

**What happens:**
1. Creates AccessToken instance
2. Adds user_id to payload
3. Adds expiration (7 days from now)
4. Signs with SECRET_KEY
5. Returns encoded string

**Token Lifetime:**
```python
# settings.py
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=7),
}
```

---

## 3. Registration Process

### RegisterSerializer

**File:** `apps/api/serializers/auth.py`

```python
class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = User
        fields = ['email', 'name', 'password', 'phone']
        extra_kwargs = {
            'phone': {'required': False}
        }
    
    def validate_email(self, value):
        """Check if email already exists"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "User with this email already exists."
            )
        return value.lower()
    
    def create(self, validated_data):
        """Create new user with hashed password"""
        user = User.objects.create_user(
            email=validated_data['email'],
            name=validated_data['name'],
            password=validated_data['password'],
            phone=validated_data.get('phone', '')
        )
        return user
```

### Line-by-Line Breakdown

**1. Password Field**
```python
password = serializers.CharField(
    write_only=True,           # Never include in response
    required=True,              # Must be provided
    validators=[validate_password],  # Django password validation
    style={'input_type': 'password'}  # UI hint
)
```

**2. validate_password (Django Built-in)**
```python
# Checks:
- Minimum 8 characters
- Not too similar to user info
- Not common password ("password123")
- Not entirely numeric
```

**3. Email Validation**
```python
def validate_email(self, value):
    if User.objects.filter(email=value).exists():
        raise serializers.ValidationError("Email already exists")
    return value.lower()
```
- **Check uniqueness:** Query database
- **Normalize:** Convert to lowercase
- **Prevent duplicates:** User@example.com ≠ user@example.com

**4. Create User**
```python
def create(self, validated_data):
    user = User.objects.create_user(  # Uses UserManager
        email=validated_data['email'],
        name=validated_data['name'],
        password=validated_data['password'],
        phone=validated_data.get('phone', '')
    )
    return user
```

### RegisterView

**File:** `apps/api/views/auth.py`

```python
class RegisterView(APIView):
    permission_classes = [AllowAny]  # No authentication required
    
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()  # Calls create()
            token = generate_jwt_token(user)
            
            return Response({
                'user': UserSerializer(user).data,
                'token': token
            }, status=status.HTTP_201_CREATED)
        
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
```

### Example Request/Response

**Request:**
```http
POST /api/auth/register/
Content-Type: application/json

{
  "email": "john@example.com",
  "name": "John Doe",
  "password": "SecurePass123!",
  "phone": "+8801712345678"
}
```

**Success Response (201):**
```json
{
  "user": {
    "id": 1,
    "email": "john@example.com",
    "name": "John Doe",
    "phone": "+8801712345678",
    "date_joined": "2025-11-23T10:30:00Z"
  },
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Error Response (400):**
```json
{
  "email": ["User with this email already exists."],
  "password": ["This password is too common."]
}
```

---

## 4. Login Process

### LoginSerializer

```python
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    
    def validate(self, attrs):
        """Validate credentials and return user"""
        email = attrs.get('email', '').lower()
        password = attrs.get('password')
        
        if email and password:
            user = authenticate(
                request=self.context.get('request'),
                username=email,  # Django's authenticate uses 'username'
                password=password
            )
            
            if not user:
                raise serializers.ValidationError(
                    {'detail': 'Invalid email or password'}
                )
            
            if not user.is_active:
                raise serializers.ValidationError(
                    {'detail': 'User account is disabled'}
                )
            
            attrs['user'] = user
            return attrs
        
        raise serializers.ValidationError(
            {'detail': 'Must include email and password'}
        )
```

### authenticate() Function

**Django's built-in authentication:**
```python
user = authenticate(username=email, password=password)
```

**What it does:**
1. Finds user by email (USERNAME_FIELD)
2. Checks password hash matches
3. Returns User object or None

**Under the hood:**
```python
# Simplified version
def authenticate(username, password):
    try:
        user = User.objects.get(email=username)
        if user.check_password(password):
            return user
    except User.DoesNotExist:
        pass
    return None
```

**check_password():**
```python
# Hashes input password and compares with stored hash
stored_hash = "pbkdf2_sha256$260000$..."
input_hash = pbkdf2_sha256(password, salt)
return input_hash == stored_hash
```

### LoginView

```python
class LoginView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token = generate_jwt_token(user)
            
            return Response({
                'user': UserSerializer(user).data,
                'token': token
            })
        
        return Response(
            serializer.errors,
            status=status.HTTP_401_UNAUTHORIZED
        )
```

### Example Request/Response

**Request:**
```http
POST /api/auth/login/
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "SecurePass123!"
}
```

**Success Response (200):**
```json
{
  "user": {
    "id": 1,
    "email": "john@example.com",
    "name": "John Doe",
    "phone": "+8801712345678",
    "date_joined": "2025-11-23T10:30:00Z"
  },
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Error Response (401):**
```json
{
  "detail": "Invalid email or password"
}
```

---

## 5. Protected Routes

### Making Endpoint Require Authentication

```python
from rest_framework.permissions import IsAuthenticated

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]  # ← Requires auth
    
    def get(self, request):
        # request.user is authenticated User object
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
```

### How It Works

**1. Client Sends Request:**
```http
GET /api/auth/profile/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJ...
```

**2. DRF Authentication Middleware:**
```python
# From settings.py
'DEFAULT_AUTHENTICATION_CLASSES': [
    'rest_framework_simplejwt.authentication.JWTAuthentication',
]
```

**3. JWTAuthentication Process:**
```python
# Simplified
class JWTAuthentication:
    def authenticate(self, request):
        # 1. Get token from header
        header = request.META.get('HTTP_AUTHORIZATION')
        # "Bearer eyJ0eXAiOiJKV1QiLCJ..."
        
        # 2. Extract token
        token = header.split(' ')[1]
        
        # 3. Decode and verify
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        
        # 4. Check expiration
        if payload['exp'] < current_time():
            raise AuthenticationFailed('Token expired')
        
        # 5. Load user
        user = User.objects.get(id=payload['user_id'])
        
        # 6. Return user
        return (user, token)
```

**4. Set request.user:**
```python
request.user = authenticated_user
request.auth = token
```

**5. Check Permissions:**
```python
class IsAuthenticated:
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
```

**6. If unauthorized:**
```json
// 401 Unauthorized
{
  "detail": "Authentication credentials were not provided."
}
```

---

## 6. Password Management

### Change Password

```python
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(
        required=True,
        validators=[validate_password]
    )
    
    def validate_old_password(self, value):
        """Verify old password is correct"""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect")
        return value
    
    def save(self):
        """Update user password"""
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user
```

**Request:**
```http
POST /api/auth/change-password/
Authorization: Bearer <token>

{
  "old_password": "OldPass123!",
  "new_password": "NewSecurePass456!"
}
```

---

## 7. Address Management

### Address Model

```python
class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    label = models.CharField(max_length=50)  # "Home", "Office"
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default='Bangladesh')
    phone = models.CharField(max_length=20)
    is_default_billing = models.BooleanField(default=False)
    is_default_shipping = models.BooleanField(default=False)
```

### Default Address Logic

**Problem:** User should only have ONE default billing and ONE default shipping address

**Solution:** Custom save method
```python
def save(self, *args, **kwargs):
    if self.is_default_billing:
        # Unset all other default billing addresses
        Address.objects.filter(
            user=self.user,
            is_default_billing=True
        ).exclude(pk=self.pk).update(is_default_billing=False)
    
    if self.is_default_shipping:
        # Unset all other default shipping addresses
        Address.objects.filter(
            user=self.user,
            is_default_shipping=True
        ).exclude(pk=self.pk).update(is_default_shipping=False)
    
    super().save(*args, **kwargs)
```

---

## 8. Security Best Practices

### Password Security

✅ **Use validate_password**
```python
from django.contrib.auth.password_validation import validate_password

password = serializers.CharField(validators=[validate_password])
```

✅ **Never store plain passwords**
```python
user.set_password(password)  # Always use this
# NOT: user.password = password
```

✅ **Hash algorithm**
```python
# Django default: PBKDF2 with SHA256
# 260,000 iterations (as of Django 4.1)
# Automatically salted
```

### JWT Security

✅ **Secret Key**
```python
# Keep SECRET_KEY secret!
# Use environment variables
SECRET_KEY = os.getenv('SECRET_KEY')
```

✅ **Token Expiration**
```python
# Don't make tokens last forever
'ACCESS_TOKEN_LIFETIME': timedelta(days=7)
```

✅ **HTTPS Only (Production)**
```python
# Force HTTPS
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

### Email Security

✅ **Normalize emails**
```python
email = self.normalize_email(email)  # Lowercase domain
```

✅ **Email verification (Future)**
```python
# Send verification email after registration
# User must verify before full access
```

---

**Continue to `05_CART_SYSTEM.md` for shopping cart implementation details.**
