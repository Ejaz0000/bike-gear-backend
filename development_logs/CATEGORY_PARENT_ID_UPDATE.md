# Category Parent ID Implementation

**Date:** November 13, 2025

## Overview
Added `parent_id` field to all category API responses to support hierarchical category structures (parent/child relationships).

## Changes Made

### 1. CategorySerializer (catalog.py)
**File:** `apps/api/serializers/catalog.py`

Added `parent_id` field to CategorySerializer:
```python
parent_id = serializers.IntegerField(source='parent.id', read_only=True, allow_null=True)
```

**Updated fields list:**
```python
fields = ['id', 'name', 'slug', 'description', 'image', 'parent_id', 'product_count']
```

### 2. HomepageCategorySerializer (homepage.py)
**File:** `apps/api/serializers/homepage.py`

Added `parent_id` field to HomepageCategorySerializer:
```python
parent_id = serializers.IntegerField(source='parent.id', read_only=True, allow_null=True)
```

**Updated fields list:**
```python
fields = ['id', 'name', 'slug', 'description', 'image_url', 'parent_id', 'product_count']
```

## API Response Examples

### Top-Level Category (No Parent)
```json
{
  "id": 1,
  "name": "Helmets",
  "slug": "helmets",
  "description": "Safety helmets for bike riders",
  "image": "http://localhost:8000/media/categories/helmets.jpg",
  "parent_id": null,
  "product_count": 12
}
```

### Sub-Category (Has Parent)
```json
{
  "id": 5,
  "name": "Mountain Bike Helmets",
  "slug": "mountain-bike-helmets",
  "description": "Helmets designed for mountain biking",
  "image": "http://localhost:8000/media/categories/mtb-helmets.jpg",
  "parent_id": 1,
  "product_count": 5
}
```

## Affected Endpoints

1. **GET /api/categories/** - List all categories
   - Now includes `parent_id` for each category
   
2. **GET /api/categories/{slug}/** - Category detail
   - Now includes `parent_id` in response
   
3. **GET /api/homepage/** - Homepage data
   - Categories in homepage response now include `parent_id`

## Frontend Integration Guide

### Building Category Tree
```javascript
// Example: Build category tree from flat list
const buildCategoryTree = (categories) => {
  const categoryMap = {};
  const rootCategories = [];
  
  // First pass: create map
  categories.forEach(cat => {
    categoryMap[cat.id] = { ...cat, children: [] };
  });
  
  // Second pass: build tree
  categories.forEach(cat => {
    if (cat.parent_id === null) {
      rootCategories.push(categoryMap[cat.id]);
    } else {
      if (categoryMap[cat.parent_id]) {
        categoryMap[cat.parent_id].children.push(categoryMap[cat.id]);
      }
    }
  });
  
  return rootCategories;
};
```

### Usage Example
```javascript
import api from './api';

// Fetch categories
const response = await api.get('categories/');
const categories = response.data;

// Build tree structure
const categoryTree = buildCategoryTree(categories);

// Render nested menu
const CategoryMenu = ({ categories }) => (
  <ul>
    {categories.map(category => (
      <li key={category.id}>
        <a href={`/category/${category.slug}`}>
          {category.name}
        </a>
        {category.children.length > 0 && (
          <CategoryMenu categories={category.children} />
        )}
      </li>
    ))}
  </ul>
);
```

## Benefits

1. **Hierarchical Navigation:** Frontend can build multi-level category menus
2. **Breadcrumbs:** Easy to generate category breadcrumbs
3. **Filtering:** Can filter products by parent category and all its children
4. **SEO:** Better URL structure with category hierarchies
5. **Flexibility:** Null value for top-level categories, integer for sub-categories

## Database Structure

The Category model already has the parent field:
```python
parent = models.ForeignKey(
    'self',
    on_delete=models.CASCADE,
    null=True,
    blank=True,
    related_name='children',
    verbose_name='Parent Category',
    help_text='Leave empty for top-level category'
)
```

## Notes

- `parent_id` is **read-only** in the API
- Returns `null` for top-level categories (no parent)
- Returns integer ID for sub-categories
- No additional database queries needed (uses existing relationship)
- Compatible with existing category structure
- No breaking changes - just adds a new field

## Testing

Test the API responses:

```bash
# Test categories list
curl http://localhost:8000/api/categories/

# Test category detail
curl http://localhost:8000/api/categories/helmets/

# Test homepage (includes categories)
curl http://localhost:8000/api/homepage/
```

## Documentation Updated

- ✅ `API_ENDPOINTS_LIST.md` - Updated with parent_id examples
- ✅ Category list endpoint documentation
- ✅ Category detail endpoint documentation
- ✅ Homepage endpoint documentation

---

**Status:** ✅ **COMPLETED & READY FOR USE**

All category API endpoints now include `parent_id` field for building hierarchical category structures.
