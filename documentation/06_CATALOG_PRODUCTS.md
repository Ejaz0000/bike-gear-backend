# 06 - Catalog & Product Management System

**Last Updated:** November 23, 2025

This guide covers the product catalog system, including products, categories, brands, variants, attributes, images, and stock management.

---

## 📋 Table of Contents

1. [System Overview](#system-overview)
2. [Database Models](#database-models)
3. [Category System](#category-system)
4. [Brand Management](#brand-management)
5. [Product Model](#product-model)
6. [Product Variants](#product-variants)
7. [Attribute System](#attribute-system)
8. [Image Management](#image-management)
9. [Stock Management](#stock-management)
10. [Serializers](#serializers)
11. [API Views](#api-views)
12. [Common Operations](#common-operations)

---

## System Overview

### What is the Catalog System?

The catalog system manages all product-related data in the e-commerce platform:

```
Catalog System
├── Categories (Hierarchical tree structure)
├── Brands (Manufacturer information)
├── Products (Base product info)
│   ├── Variants (Size, color combinations)
│   ├── Images (Multiple images per product)
│   └── Attributes (Flexible product properties)
└── Stock (Real-time inventory tracking)
```

### Key Features

- **Hierarchical Categories**: Parent-child category relationships
- **Product Variants**: Different sizes, colors, materials
- **Flexible Attributes**: Custom product properties (Size, Color, Material, etc.)
- **Multiple Images**: Primary and gallery images
- **Stock Tracking**: Real-time inventory management
- **SEO Fields**: Meta titles and descriptions
- **Price Management**: Regular and sale prices

---

## Database Models

### Model Relationships

```
┌─────────────┐
│  Category   │──┐
└─────────────┘  │
                 │ One-to-Many
                 ▼
┌─────────────┐  ┌─────────────┐
│    Brand    │  │   Product   │
└─────────────┘  └─────────────┘
      │               │
      │               ├──────────────┐
      │               │              │
      └───────────────┘              │
         One-to-Many         One-to-Many
                                     │
                 ┌──────────┬────────┴─────────┬────────────┐
                 │          │                  │            │
           ┌─────▼────┐ ┌───▼──────┐ ┌────────▼────┐ ┌─────▼─────┐
           │  Variant │ │  Image   │ │ AttributeType│ │   Stock   │
           └──────────┘ └──────────┘ └──────────────┘ └───────────┘
                │                           │
                │                           │
                └───────────┬───────────────┘
                     Many-to-Many
                            │
                    ┌───────▼──────┐
                    │AttributeValue│
                    └──────────────┘
```

---

## Category System

### Category Model

**File:** `apps/catalog/models.py`

```python
class Category(models.Model):
    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='Category Name'
    )
    # 'name': Human-readable category name
    # 'unique=True': No duplicate category names allowed
    # Example: "Mountain Bikes", "Road Bikes"
    
    slug = models.SlugField(
        max_length=200,
        unique=True,
        db_index=True,
        help_text='URL-friendly version of name'
    )
    # 'slug': URL-safe version of the name
    # 'db_index=True': Fast lookups when browsing by category
    # Example: name="Mountain Bikes" → slug="mountain-bikes"

    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name='Parent Category',
        help_text='Leave empty for top-level category'
    )
    # 'self': Points to another Category (hierarchical structure)
    # 'null=True': Top-level categories don't have a parent
    # 'related_name="children"': Access subcategories via parent.children.all()
    # Example: parent="Bikes" → children=["Mountain Bikes", "Road Bikes"]

    description = models.TextField(
        blank=True,
        help_text='Category description for SEO'
    )
    
    image = models.ImageField(
        upload_to='categories/',
        blank=True,
        null=True,
        help_text='Category banner image'
    )
    # 'upload_to': Saves to MEDIA_ROOT/categories/
    # Used for category landing pages

    is_active = models.BooleanField(
        default=True,
        help_text='Inactive categories are hidden from storefront'
    )
    # Soft delete: Don't delete data, just hide it
    
    display_order = models.IntegerField(
        default=0,
        help_text='Lower numbers appear first'
    )
    # Sort categories: 0, 1, 2, 3...
    # Useful for featuring popular categories first

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    # Auto-generate slug from name if not provided
    # "Mountain Bikes" → "mountain-bikes"

    class Meta:
        db_table = 'categories'
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['display_order','name']
    # Custom table name and ordering

    def __str__(self):
        return self.name
```

### Category Hierarchy Example

```python
# Creating a hierarchical category structure:

# Top-level category
bikes = Category.objects.create(
    name="Bikes",
    slug="bikes",
    description="All types of bicycles",
    display_order=1
)

# Subcategories
mountain = Category.objects.create(
    name="Mountain Bikes",
    slug="mountain-bikes",
    parent=bikes,  # Child of "Bikes"
    display_order=1
)

road = Category.objects.create(
    name="Road Bikes",
    slug="road-bikes",
    parent=bikes,
    display_order=2
)

# Query examples:
# Get all top-level categories (no parent)
top_categories = Category.objects.filter(parent=None)

# Get all subcategories of "Bikes"
subcategories = bikes.children.all()  # [Mountain Bikes, Road Bikes]

# Get parent of "Mountain Bikes"
parent_category = mountain.parent  # "Bikes"
```

---

## Brand Management

### Brand Model

**File:** `apps/catalog/models.py`

```python
class Brand(models.Model):
    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='Brand Name'
    )
    # Example: "Trek", "Specialized", "Giant"

    slug = models.SlugField(
        max_length=200,
        unique=True,
        db_index=True
    )
    # URL-friendly: "trek", "specialized", "giant"

    description = models.TextField(
        blank=True,
        help_text='Brand description'
    )
    # Marketing content about the brand

    logo = models.ImageField(
        upload_to='brands/',
        blank=True,
        null=True,
        help_text='Brand logo'
    )
    # Saves to MEDIA_ROOT/brands/
    # Displayed on brand pages and product listings

    website = models.URLField(
        blank=True,
        help_text='Brand website URL'
    )
    # Example: "https://www.trekbikes.com"

    is_active = models.BooleanField(
        default=True,
        help_text='Inactive brands are hidden from storefront'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'brands'
        verbose_name = 'Brand'
        verbose_name_plural = 'Brands'
        ordering = ['name']

    def __str__(self):
        return self.name
```

### Brand Usage Example

```python
# Creating a brand
trek = Brand.objects.create(
    name="Trek",
    slug="trek",
    description="American bicycle manufacturer",
    website="https://www.trekbikes.com"
)

# Get all products by this brand
trek_products = trek.products.all()

# Count products per brand
from django.db.models import Count
brands_with_counts = Brand.objects.annotate(
    product_count=Count('products')
).filter(product_count__gt=0)
```

---

## Product Model

### Product Model Structure

**File:** `apps/catalog/models.py`

```python
class Product(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name='Product Title'
    )
    # Example: "Trek Marlin 7 Mountain Bike"

    slug = models.SlugField(
        max_length=255,
        unique=True,
        db_index=True,
        help_text='URL-friendly version of title'
    )
    # URL: /products/trek-marlin-7-mountain-bike/

    brand = models.ForeignKey(
        Brand,
        on_delete=models.SET_NULL,
        related_name='products',
        null=True,
        blank=True,
        related_query_name='products'
    )
    # 'SET_NULL': If brand is deleted, keep product but set brand=NULL
    # 'related_name': brand.products.all()

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='products',
        null=True,
        blank=True,
        related_query_name='products'
    )
    # Links product to a category

    description = models.TextField(
        blank=True,
        help_text='Product description'
    )
    # Rich text description of the product
    # Example: "The Trek Marlin 7 is the perfect gateway..."

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='Product Price',
        help_text='Base/starting price (variants may differ)'
    )
    # max_digits=10: Up to 99,999,999.99
    # decimal_places=2: Two decimal places (cents)
    # Example: 799.99

    sale_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        blank=True,
        null=True,
        verbose_name='Sale Price',
        help_text='Sale price (optional)'
    )
    # If set, display this instead of regular price
    # Example: Regular: $799.99, Sale: $699.99

    stock = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text='Total stock across all variants (informational only)'
    )
    # Note: Actual stock is tracked per variant
    # This is a summary field

    low_stock_threshold = models.IntegerField(
        default=5,
        help_text='Alert when stock falls below this number'
    )
    # Email notification when stock <= 5

    # Physical dimensions for shipping
    weight = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Weight in kg'
    )
    
    length = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Length in cm'
    )
    
    width = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Width in cm'
    )
    
    height = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Height in cm'
    )

    is_active = models.BooleanField(
        default=True,
        help_text='Inactive products are hidden from storefront'
    )

    # SEO fields
    meta_title = models.CharField(
        max_length=200,
        blank=True,
        help_text='SEO page title'
    )
    # Shown in browser tab and search results
    
    meta_description = models.CharField(
        max_length=300,
        blank=True,
        help_text='SEO meta description'
    )
    # Shown in search results snippet

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'products'
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active', '-created_at']),
        ]
    # Indexes for fast queries on slug and active products

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('product-detail', kwargs={'slug': self.slug})

    def get_total_stock(self):
        """Calculate total stock across all variants."""
        total = self.variants.filter(is_active=True).aggregate(
            total_stock=models.Sum('stock')
        )['total_stock']
        return total if total else 0
    # Sum stock of all active variants
    # Example: Small (5) + Medium (10) + Large (3) = 18
    
    def is_in_stock(self):
        """Check if any variant is in stock."""
        return self.variants.filter(is_active=True, stock__gt=0).exists()
    # Returns True if any variant has stock > 0
    
    def is_low_stock(self):
        """Check if total stock is below threshold."""
        total = self.get_total_stock()
        return 0 < total <= self.low_stock_threshold
    # Returns True if 0 < stock <= 5
```

### Product Creation Example

```python
# Creating a product
product = Product.objects.create(
    title="Trek Marlin 7 Mountain Bike",
    slug="trek-marlin-7-mountain-bike",
    brand=trek,  # Brand instance
    category=mountain,  # Category instance
    description="Perfect gateway to trail riding...",
    price=Decimal('799.99'),
    sale_price=Decimal('699.99'),
    stock=15,
    weight=Decimal('13.5'),
    meta_title="Trek Marlin 7 - Mountain Bike for Sale",
    meta_description="Buy the Trek Marlin 7 mountain bike..."
)

# Check stock status
if product.is_in_stock():
    print("Product available")

if product.is_low_stock():
    print("Low stock alert!")

total_stock = product.get_total_stock()
```

---

## Product Variants

### Why Variants?

Variants allow a single product to have multiple options:

```
Product: "T-Shirt"
├── Variant 1: Small, Red, $19.99, Stock: 10
├── Variant 2: Small, Blue, $19.99, Stock: 5
├── Variant 3: Medium, Red, $19.99, Stock: 8
├── Variant 4: Medium, Blue, $19.99, Stock: 12
└── Variant 5: Large, Red, $24.99, Stock: 3
```

### ProductVariant Model

**File:** `apps/catalog/models.py`

```python
class ProductVariant(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='variants'
    )
    # CASCADE: If product is deleted, delete all its variants
    # Access via: product.variants.all()

    sku = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        help_text='Unique identifier for the variant'
    )
    # Stock Keeping Unit - unique identifier
    # Example: "TREK-MARL7-RED-M" for Trek Marlin 7, Red, Medium
    # 'unique=True': Each SKU must be unique across ALL products

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text='Price of the variant'
    )
    # Variant can have different price than base product
    # Example: Large size costs more than Small

    sale_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        null=True,
        blank=True,
        help_text='Sale price of the variant'
    )
    # Optional discounted price for this variant

    stock = models.PositiveIntegerField(
        default=0,
        help_text='Available stock for the variant'
    )
    # CRITICAL: Each variant tracks its own stock
    # This is the ACTUAL inventory count
    # PositiveIntegerField: Cannot be negative

    weight = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Weight in kg'
    )
    # Some variants may weigh differently

    is_active = models.BooleanField(
        default=True,
        help_text='Inactive variants are hidden from storefront'
    )
    # Temporarily disable without deleting

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'product_variants'
        verbose_name = 'Product Variant'
        verbose_name_plural = 'Product Variants'
        ordering = ['product', 'sku']

    def __str__(self):
        return f"{self.product.title} - {self.sku}"

    def get_effective_price(self):
        """Get the price to display (sale price if available)"""
        if self.sale_price is not None:
            return self.sale_price
        return self.price
    # Returns: sale_price if set, otherwise regular price

    def get_attributes_display(self):
        """Get human-readable attribute string"""
        attrs = self.attributes.select_related(
            'attribute_value__attribute_type'
        ).order_by('attribute_value__attribute_type__display_order')
        return ' / '.join([f"{av.attribute_value.value}" for av in attrs])
    # Returns: "Red / Medium / Cotton"

    def is_in_stock(self):
        return self.stock > 0
    
    def is_on_sale(self):
        return self.sale_price is not None
```

### Variant Example

```python
# Create variants for a T-Shirt product
tshirt = Product.objects.get(slug="basic-tshirt")

# Small Red variant
variant1 = ProductVariant.objects.create(
    product=tshirt,
    sku="TSHIRT-SM-RED",
    price=Decimal('19.99'),
    stock=10
)

# Medium Blue variant
variant2 = ProductVariant.objects.create(
    product=tshirt,
    sku="TSHIRT-MD-BLUE",
    price=Decimal('19.99'),
    sale_price=Decimal('14.99'),  # On sale!
    stock=5
)

# Large Red variant (costs more)
variant3 = ProductVariant.objects.create(
    product=tshirt,
    sku="TSHIRT-LG-RED",
    price=Decimal('24.99'),
    stock=3
)

# Query examples:
# Get all variants of a product
variants = tshirt.variants.all()

# Get in-stock variants only
in_stock = tshirt.variants.filter(stock__gt=0, is_active=True)

# Get variants on sale
on_sale = tshirt.variants.filter(sale_price__isnull=False)

# Get variant by SKU
variant = ProductVariant.objects.get(sku="TSHIRT-SM-RED")
```

---

## Attribute System

### How Attributes Work

Attributes define variant characteristics:

```
AttributeType: "Size"
├── AttributeValue: "Small"
├── AttributeValue: "Medium"
└── AttributeValue: "Large"

AttributeType: "Color"
├── AttributeValue: "Red"
├── AttributeValue: "Blue"
└── AttributeValue: "Green"

Variant: TSHIRT-SM-RED
├── VariantAttribute → Size: Small
└── VariantAttribute → Color: Red
```

### AttributeType Model

**File:** `apps/catalog/models.py`

```python
class AttributeType(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text='E.g., Color, Size, Material'
    )
    # Attribute category name
    # Example: "Size", "Color", "Material", "Style"

    slug = models.SlugField(
        unique=True,
        help_text='URL-friendly name'
    )
    # Example: "size", "color", "material"

    display_order = models.IntegerField(
        default=0,
        help_text='Order in which attributes are shown'
    )
    # Show Size first (0), then Color (1), then Material (2)

    class Meta:
        db_table = 'attribute_types'
        verbose_name = 'Attribute Type'
        verbose_name_plural = 'Attribute Types'
        ordering = ['display_order','name']

    def __str__(self):
        return self.name
    
    def save(self,*args,**kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args,**kwargs)
```

### AttributeValue Model

```python
class AttributeValue(models.Model):
    attribute_type = models.ForeignKey(
        AttributeType,
        on_delete=models.CASCADE,
        related_name='values',
    )
    # Links value to its type
    # Example: attribute_type="Size", value="Medium"

    value = models.CharField(
        max_length=200,
        help_text='E.g., Red, Blue, Medium'
    )
    # The actual value
    # Example: "Red", "Large", "Cotton"

    display_order = models.IntegerField(
        default=0,
        help_text='Order in which values are shown'
    )
    # Show values in logical order (XS, S, M, L, XL)

    class Meta:
        db_table = 'attribute_values'
        verbose_name = 'Attribute Value'
        verbose_name_plural = 'Attribute Values'
        ordering = ['attribute_type','display_order','value']
        unique_together = ['attribute_type', 'value']
    # unique_together: Can't have duplicate "Size: Medium"

    def __str__(self):
        return f"{self.attribute_type.name}: {self.value}"
    # Returns: "Size: Medium" or "Color: Red"
```

### VariantAttribute (Junction Table)

```python
class VariantAttribute(models.Model):
    """
    Junction table linking variants to attribute values.
    E.g., Variant 1 = {Color: Red, Size: Medium}
    """
    product_variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        related_name='attributes'
    )
    # The variant this attribute belongs to

    attribute_value = models.ForeignKey(
        AttributeValue,
        on_delete=models.CASCADE
    )
    # The attribute value (e.g., "Red", "Medium")

    class Meta:
        db_table = 'variant_attributes'
        verbose_name = 'Variant Attribute'
        verbose_name_plural = 'Variant Attributes'
        unique_together = ['product_variant', 'attribute_value']
    # unique_together: A variant can't have "Red" twice

    def __str__(self):
        return f"{self.product_variant} - {self.attribute_value}"
```

### Complete Attribute Example

```python
# 1. Create Attribute Types
size_type = AttributeType.objects.create(
    name="Size",
    slug="size",
    display_order=0
)

color_type = AttributeType.objects.create(
    name="Color",
    slug="color",
    display_order=1
)

# 2. Create Attribute Values
small = AttributeValue.objects.create(
    attribute_type=size_type,
    value="Small",
    display_order=0
)

medium = AttributeValue.objects.create(
    attribute_type=size_type,
    value="Medium",
    display_order=1
)

red = AttributeValue.objects.create(
    attribute_type=color_type,
    value="Red",
    display_order=0
)

blue = AttributeValue.objects.create(
    attribute_type=color_type,
    value="Blue",
    display_order=1
)

# 3. Create Product and Variant
tshirt = Product.objects.create(
    title="Basic T-Shirt",
    slug="basic-tshirt",
    price=Decimal('19.99')
)

variant = ProductVariant.objects.create(
    product=tshirt,
    sku="TSHIRT-SM-RED",
    price=Decimal('19.99'),
    stock=10
)

# 4. Link Attributes to Variant
VariantAttribute.objects.create(
    product_variant=variant,
    attribute_value=small
)

VariantAttribute.objects.create(
    product_variant=variant,
    attribute_value=red
)

# 5. Query variant attributes
attrs = variant.attributes.all()
for attr in attrs:
    print(f"{attr.attribute_value.attribute_type.name}: {attr.attribute_value.value}")
# Output:
# Size: Small
# Color: Red

# Get human-readable display
display = variant.get_attributes_display()
# Returns: "Small / Red"
```

---

## Image Management

### ProductImage Model

**File:** `apps/catalog/models.py`

```python
class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images'
    )
    # CASCADE: Delete images when product is deleted
    # Access via: product.images.all()

    image = models.ImageField(
        upload_to='products/%Y/%m/',
        help_text='Product image'
    )
    # Organized by date: products/2025/11/image.jpg
    # %Y = year (2025)
    # %m = month (11)

    alt_text = models.CharField(
        max_length=200,
        blank=True,
        help_text='Alternative text for accessibility'
    )
    # For screen readers and SEO
    # Example: "Trek Marlin 7 Mountain Bike - Front View"

    position = models.IntegerField(
        default=0,
        help_text='Display order (0 = primary image)'
    )
    # position=0: Primary/thumbnail image
    # position=1,2,3: Gallery images

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'product_images'
        verbose_name = 'Product Image'
        verbose_name_plural = 'Product Images'
        ordering = ['position']
    # Always return images in position order

    def __str__(self):
        return f"Image for {self.product.title} - Image {self.position}"

    def save(self,*args,**kwargs):
        if not self.alt_text:
            self.alt_text = f"{self.product.title} - Image {self.position + 1}"
        super().save(*args,**kwargs)
    # Auto-generate alt_text if not provided
```

### Image Usage Example

```python
# Add multiple images to a product
product = Product.objects.get(slug="trek-marlin-7")

# Primary image (position=0)
primary = ProductImage.objects.create(
    product=product,
    image='path/to/image1.jpg',
    alt_text="Trek Marlin 7 - Front View",
    position=0
)

# Gallery images
ProductImage.objects.create(
    product=product,
    image='path/to/image2.jpg',
    alt_text="Trek Marlin 7 - Side View",
    position=1
)

ProductImage.objects.create(
    product=product,
    image='path/to/image3.jpg',
    alt_text="Trek Marlin 7 - Detail Shot",
    position=2
)

# Query examples:
# Get primary image
primary_image = product.images.filter(position=0).first()

# Get all gallery images
gallery = product.images.filter(position__gt=0)

# Get all images in order
all_images = product.images.all()  # Already ordered by position
```

---

## Stock Management

### How Stock is Tracked

```
Product: Trek Marlin 7
├── Variant: Small, Red (SKU: TREK-M7-SM-RED)
│   └── Stock: 5 units
├── Variant: Medium, Red (SKU: TREK-M7-MD-RED)
│   └── Stock: 10 units
└── Variant: Large, Blue (SKU: TREK-M7-LG-BLUE)
    └── Stock: 0 units (OUT OF STOCK)

Total Product Stock: 5 + 10 + 0 = 15 units
```

### Stock Operations

```python
from django.db import transaction

# 1. Check stock before adding to cart
variant = ProductVariant.objects.get(sku="TREK-M7-SM-RED")

if variant.is_in_stock():
    print(f"Available: {variant.stock} units")
else:
    print("Out of stock")

# 2. Reserve stock when adding to cart (decreases stock)
@transaction.atomic
def add_to_cart(variant_id, quantity):
    variant = ProductVariant.objects.select_for_update().get(id=variant_id)
    # select_for_update(): Database-level lock to prevent race conditions
    
    if variant.stock >= quantity:
        variant.stock -= quantity
        variant.save()
        # Create cart item here...
        return True
    else:
        raise ValueError("Insufficient stock")

# 3. Release stock when removing from cart (increases stock)
@transaction.atomic
def remove_from_cart(variant_id, quantity):
    variant = ProductVariant.objects.select_for_update().get(id=variant_id)
    variant.stock += quantity
    variant.save()

# 4. Low stock alert
low_stock_variants = ProductVariant.objects.filter(
    stock__gt=0,
    stock__lte=5,
    is_active=True
).select_related('product')

for variant in low_stock_variants:
    print(f"LOW STOCK: {variant.product.title} - {variant.sku}: {variant.stock} units")

# 5. Out of stock products
out_of_stock = Product.objects.filter(
    variants__stock=0,
    variants__is_active=True
).distinct()
```

### Stock Validation

```python
# In API view or cart logic
from rest_framework.exceptions import ValidationError

def validate_stock(variant, requested_quantity):
    """Validate if requested quantity is available"""
    if not variant.is_active:
        raise ValidationError("This variant is no longer available")
    
    if variant.stock < requested_quantity:
        raise ValidationError(
            f"Only {variant.stock} units available. You requested {requested_quantity}."
        )
    
    if variant.stock == 0:
        raise ValidationError("This item is out of stock")
    
    return True
```

---

## Serializers

### CategorySerializer

**File:** `apps/api/serializers/catalog.py`

```python
class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category model"""
    product_count = serializers.SerializerMethodField()
    parent_id = serializers.IntegerField(source='parent.id', read_only=True, allow_null=True)
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'image', 'parent_id', 'product_count']
    
    def get_product_count(self, obj):
        """Get active product count for category"""
        return obj.products.filter(is_active=True).count()
```

**Response Example:**

```json
{
  "id": 1,
  "name": "Mountain Bikes",
  "slug": "mountain-bikes",
  "description": "All-terrain bicycles for trail riding",
  "image": "http://example.com/media/categories/mountain.jpg",
  "parent_id": null,
  "product_count": 15
}
```

### ProductListSerializer

```python
class ProductListSerializer(serializers.ModelSerializer):
    """Serializer for Product List"""
    category = CategorySerializer(read_only=True)
    brand = BrandSerializer(read_only=True)
    primary_image = serializers.SerializerMethodField()
    min_price = serializers.SerializerMethodField()
    max_price = serializers.SerializerMethodField()
    is_on_sale = serializers.SerializerMethodField()
    discount_percentage = serializers.SerializerMethodField()
    variant_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'title', 'slug', 'category', 'brand', 'price', 'sale_price',
            'min_price', 'max_price', 'is_on_sale', 'discount_percentage',
            'stock', 'primary_image', 'variant_count'
        ]
    
    def get_primary_image(self, obj):
        """Get primary product image URL"""
        request = self.context.get('request')
        image = obj.images.filter(position=0).first()
        if image and image.image:
            return request.build_absolute_uri(image.image.url) if request else image.image.url
        return None
    # Returns full URL: http://example.com/media/products/2025/11/image.jpg
    
    def get_min_price(self, obj):
        """Get minimum price from variants"""
        variants = obj.variants.all()
        if variants:
            prices = [v.sale_price if v.sale_price else v.price for v in variants]
            return min(prices) if prices else obj.price
        return obj.price
    # If variants exist, return lowest variant price
    # Otherwise return product base price
    
    def get_discount_percentage(self, obj):
        """Calculate maximum discount percentage"""
        discounts = []
        
        # Product level discount
        if obj.sale_price and obj.sale_price < obj.price:
            discount = ((obj.price - obj.sale_price) / obj.price) * 100
            discounts.append(discount)
        
        # Variant discounts
        for variant in obj.variants.all():
            if variant.sale_price and variant.sale_price < variant.price:
                discount = ((variant.price - variant.sale_price) / variant.price) * 100
                discounts.append(discount)
        
        return round(max(discounts), 0) if discounts else None
    # Returns highest discount percentage across all variants
    # Example: 25 (means 25% off)
```

**Response Example:**

```json
{
  "id": 1,
  "title": "Trek Marlin 7 Mountain Bike",
  "slug": "trek-marlin-7-mountain-bike",
  "category": {
    "id": 2,
    "name": "Mountain Bikes",
    "slug": "mountain-bikes"
  },
  "brand": {
    "id": 1,
    "name": "Trek",
    "slug": "trek"
  },
  "price": "799.99",
  "sale_price": "699.99",
  "min_price": "699.99",
  "max_price": "799.99",
  "is_on_sale": true,
  "discount_percentage": 13,
  "stock": 15,
  "primary_image": "http://example.com/media/products/2025/11/trek-marlin.jpg",
  "variant_count": 3
}
```

### ProductDetailSerializer

```python
class ProductDetailSerializer(serializers.ModelSerializer):
    """Detailed product serializer with all related data"""
    category = CategorySerializer(read_only=True)
    brand = BrandSerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'title', 'slug', 'description', 'category', 'brand',
            'price', 'sale_price', 'stock', 'weight', 'length', 'width', 'height',
            'meta_title', 'meta_description', 'images', 'variants',
            'created_at', 'updated_at'
        ]
```

---

## API Views

### ProductListView

**File:** `apps/api/views/catalog.py`

```python
class ProductListView(StandardResponseMixin, generics.ListAPIView):
    """
    GET /api/products/
    List all products with filtering, searching, and pagination
    """
    serializer_class = ProductListSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['price', 'created_at', 'title']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Get filtered queryset"""
        queryset = Product.objects.filter(is_active=True).select_related(
            'category', 'brand'
        ).prefetch_related('images', 'variants')
        # select_related: JOIN category and brand (ForeignKey)
        # prefetch_related: Separate queries for images and variants (Many)
        
        # Category filter - support multiple categories (comma-separated)
        category_param = self.request.query_params.get('category')
        if category_param:
            category_slugs = [slug.strip() for slug in category_param.split(',') if slug.strip()]
            if category_slugs:
                queryset = queryset.filter(category__slug__in=category_slugs)
        # Example: ?category=mountain-bikes,road-bikes
        
        # Brand filter - support multiple brands (comma-separated)
        brand_param = self.request.query_params.get('brand')
        if brand_param:
            brand_slugs = [slug.strip() for slug in brand_param.split(',') if slug.strip()]
            if brand_slugs:
                queryset = queryset.filter(brand__slug__in=brand_slugs)
        # Example: ?brand=trek,specialized
        
        # Price range filter
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        
        if min_price:
            queryset = queryset.filter(
                Q(price__gte=min_price) | Q(variants__price__gte=min_price)
            )
        # Find products OR variants with price >= min_price
        
        if max_price:
            queryset = queryset.filter(
                Q(price__lte=max_price) | Q(variants__price__lte=max_price)
            )
        # Example: ?min_price=100&max_price=500
        
        # On sale filter
        on_sale = self.request.query_params.get('on_sale')
        if on_sale and on_sale.lower() == 'true':
            queryset = queryset.filter(
                Q(sale_price__isnull=False, sale_price__lt=F('price')) |
                Q(variants__sale_price__isnull=False)
            )
        # Example: ?on_sale=true
        
        return queryset.distinct()
        # distinct(): Remove duplicate products from multiple filters
```

**API Examples:**

```bash
# Get all products
GET /api/products/

# Search products
GET /api/products/?search=trek

# Filter by category
GET /api/products/?category=mountain-bikes

# Filter by multiple categories
GET /api/products/?category=mountain-bikes,road-bikes

# Filter by brand
GET /api/products/?brand=trek

# Filter by price range
GET /api/products/?min_price=500&max_price=1000

# Filter products on sale
GET /api/products/?on_sale=true

# Sort by price
GET /api/products/?ordering=price  # Low to high
GET /api/products/?ordering=-price # High to low

# Combine filters
GET /api/products/?category=mountain-bikes&brand=trek&min_price=500&max_price=1500&ordering=price
```

### ProductDetailView

```python
class ProductDetailView(StandardResponseMixin, generics.RetrieveAPIView):
    """
    GET /api/products/{slug}/
    Get product detail by slug
    """
    serializer_class = ProductDetailSerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'
    
    def get_queryset(self):
        """Get active products with related data"""
        return Product.objects.filter(is_active=True).select_related(
            'category', 'brand'
        ).prefetch_related(
            'images', 
            'variants', 
            'variants__attributes', 
            'variants__attributes__attribute_value', 
            'variants__attributes__attribute_value__attribute_type'
        )
        # Deep prefetch to avoid N+1 queries on variant attributes
```

**API Example:**

```bash
GET /api/products/trek-marlin-7-mountain-bike/
```

**Response:**

```json
{
  "success": true,
  "data": {
    "id": 1,
    "title": "Trek Marlin 7 Mountain Bike",
    "slug": "trek-marlin-7-mountain-bike",
    "description": "The Trek Marlin 7 is the perfect gateway to trail riding...",
    "category": {
      "id": 2,
      "name": "Mountain Bikes",
      "slug": "mountain-bikes"
    },
    "brand": {
      "id": 1,
      "name": "Trek",
      "slug": "trek"
    },
    "price": "799.99",
    "sale_price": "699.99",
    "stock": 15,
    "images": [
      {
        "id": 1,
        "image": "http://example.com/media/products/2025/11/trek1.jpg",
        "alt_text": "Trek Marlin 7 - Front View",
        "position": 0
      },
      {
        "id": 2,
        "image": "http://example.com/media/products/2025/11/trek2.jpg",
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
    ]
  }
}
```

---

## Common Operations

### 1. Get Products by Category

```python
# In views or shell
category = Category.objects.get(slug="mountain-bikes")
products = category.products.filter(is_active=True)
```

### 2. Get Products by Brand

```python
brand = Brand.objects.get(slug="trek")
products = brand.products.filter(is_active=True)
```

### 3. Get Available Variants

```python
product = Product.objects.get(slug="basic-tshirt")
available_variants = product.variants.filter(
    is_active=True,
    stock__gt=0
)
```

### 4. Find Variant by Attributes

```python
# Find variant with specific attributes (e.g., Size: Medium, Color: Red)
from django.db.models import Q

product = Product.objects.get(slug="basic-tshirt")

# Get attribute values
medium = AttributeValue.objects.get(attribute_type__slug="size", value="Medium")
red = AttributeValue.objects.get(attribute_type__slug="color", value="Red")

# Find variant with both attributes
variants = product.variants.filter(
    attributes__attribute_value=medium
).filter(
    attributes__attribute_value=red
)

variant = variants.first()
```

### 5. Update Stock

```python
from django.db import transaction

@transaction.atomic
def update_stock(sku, quantity_change):
    """
    Update variant stock
    quantity_change: positive to add, negative to subtract
    """
    variant = ProductVariant.objects.select_for_update().get(sku=sku)
    new_stock = variant.stock + quantity_change
    
    if new_stock < 0:
        raise ValueError("Cannot reduce stock below 0")
    
    variant.stock = new_stock
    variant.save()
    
    return variant

# Add stock (restocking)
update_stock("TREK-M7-SM-RED", 10)  # Add 10 units

# Reduce stock (after order)
update_stock("TREK-M7-SM-RED", -2)  # Remove 2 units
```

### 6. Bulk Operations

```python
# Activate all products in a category
Category.objects.get(slug="mountain-bikes").products.update(is_active=True)

# Deactivate out-of-stock variants
ProductVariant.objects.filter(stock=0).update(is_active=False)

# Apply discount to all variants of a product
product = Product.objects.get(slug="basic-tshirt")
for variant in product.variants.all():
    variant.sale_price = variant.price * Decimal('0.8')  # 20% off
    variant.save()
```

---

## Summary

### Key Takeaways

1. **Products** are the base entity with general information
2. **Variants** handle specific combinations (size, color) with individual stock
3. **Attributes** provide flexible product properties through a type-value system
4. **Categories** support hierarchical organization (parent-child)
5. **Stock** is tracked per variant, not per product
6. **Images** are ordered by position (0 = primary)
7. **Serializers** transform models into API responses
8. **Views** handle filtering, searching, and pagination

### Best Practices

1. ✅ Always use `select_related()` and `prefetch_related()` for performance
2. ✅ Use `select_for_update()` when modifying stock to prevent race conditions
3. ✅ Validate stock availability before creating orders
4. ✅ Use slugs in URLs, not IDs (better SEO)
5. ✅ Soft delete with `is_active=False` instead of hard deletes
6. ✅ Index frequently queried fields (slug, is_active)
7. ✅ Auto-generate slugs from names to prevent errors

---

**Next:** [07_API_ENDPOINTS.md](./07_API_ENDPOINTS.md) - Complete API Reference

**Previous:** [05_CART_SYSTEM.md](./05_CART_SYSTEM.md) - Cart System Documentation
