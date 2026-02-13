"""
API Views for catalog (products, categories, brands)
"""
from rest_framework import generics, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Min, Max, F

from catalog.models import Product, Category, Brand
from core.models import FeaturedSection
from api.serializers import (
    ProductListSerializer,
    ProductDetailSerializer,
    CategorySerializer,
    CategoryDetailSerializer,
    BrandSerializer,
    BrandDetailSerializer,
    SearchResultSerializer,
    FeaturedSectionSerializer,
)
from api.utils import StandardResponseMixin, success_response, bad_request_response


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
        
        # Category filter - support multiple categories (comma-separated)
        category_param = self.request.query_params.get('category')
        if category_param:
            category_slugs = [slug.strip() for slug in category_param.split(',') if slug.strip()]
            if category_slugs:
                queryset = queryset.filter(category__slug__in=category_slugs)
        
        # Brand filter - support multiple brands (comma-separated)
        brand_param = self.request.query_params.get('brand')
        if brand_param:
            brand_slugs = [slug.strip() for slug in brand_param.split(',') if slug.strip()]
            if brand_slugs:
                queryset = queryset.filter(brand__slug__in=brand_slugs)
        
        # Price range filter
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        
        if min_price:
            queryset = queryset.filter(
                Q(price__gte=min_price) | Q(variants__price__gte=min_price)
            )
        
        if max_price:
            queryset = queryset.filter(
                Q(price__lte=max_price) | Q(variants__price__lte=max_price)
            )
        
        # Featured filter
        is_featured = self.request.query_params.get('is_featured')
        if is_featured and is_featured.lower() == 'true':
            queryset = queryset.filter(is_featured=True)
        
        # On sale filter
        on_sale = self.request.query_params.get('on_sale')
        if on_sale and on_sale.lower() == 'true':
            queryset = queryset.filter(
                Q(sale_price__isnull=False, sale_price__lt=F('price')) |
                Q(variants__sale_price__isnull=False)
            )
        
        return queryset.distinct()
    
    def list(self, request, *args, **kwargs):
        """Override list to include featured_sections in response"""
        # Call the grandparent's list method to skip StandardResponseMixin wrapper
        response = generics.ListAPIView.list(self, request, *args, **kwargs)
        
        # Get active featured sections
        featured_sections = FeaturedSection.objects.filter(
            is_active=True
        ).prefetch_related('products')
        
        featured_sections_data = FeaturedSectionSerializer(
            featured_sections,
            many=True,
            context={'request': request}
        ).data
        
        # The pagination class already wraps data, so we extract and restructure
        response_data = response.data
        if 'data' in response_data:
            # Pagination already structured the response
            response_data['featured_sections'] = featured_sections_data
            return Response(response_data, status=response.status_code)
        else:
            # No pagination, wrap manually
            return Response({
                "status": True,
                "status_code": response.status_code,
                "message": "Products retrieved successfully",
                "data": response_data,
                "featured_sections": featured_sections_data
            }, status=response.status_code)


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
        ).prefetch_related('images', 'variants', 'variants__attributes', 'variants__attributes__attribute_value', 'variants__attributes__attribute_value__attribute_type')
    
    def retrieve(self, request, *args, **kwargs):
        """Override retrieve to include featured_sections in response"""
        # Call the grandparent's retrieve method to skip StandardResponseMixin wrapper
        response = generics.RetrieveAPIView.retrieve(self, request, *args, **kwargs)
        
        # Get active featured sections
        featured_sections = FeaturedSection.objects.filter(
            is_active=True
        ).prefetch_related('products')
        
        featured_sections_data = FeaturedSectionSerializer(
            featured_sections,
            many=True,
            context={'request': request}
        ).data
        
        return Response({
            "status": True,
            "status_code": response.status_code,
            "message": "Product retrieved successfully",
            "data": response.data,
            "featured_sections": featured_sections_data
        }, status=response.status_code)


class CategoryListView(StandardResponseMixin, generics.ListAPIView):
    """
    GET /api/categories/
    List all active categories 
    """
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
    queryset = Category.objects.filter(is_active=True).prefetch_related('products')
    pagination_class = None  # No pagination for categories


class CategoryDetailView(StandardResponseMixin, generics.RetrieveAPIView):
    """
    GET /api/categories/{slug}/
    Get category detail with products
    """
    serializer_class = CategoryDetailSerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'
    
    def get_queryset(self):
        """Get active categories with active products"""
        return Category.objects.filter(is_active=True).prefetch_related(
            'products__images',
            'products__brand',
            'products__variants'
        )


class BrandListView(StandardResponseMixin, generics.ListAPIView):
    """
    GET /api/brands/
    List all active brands
    """
    serializer_class = BrandSerializer
    permission_classes = [AllowAny]
    queryset = Brand.objects.filter(is_active=True).prefetch_related('products')
    pagination_class = None  # No pagination for brands


class BrandDetailView(StandardResponseMixin, generics.RetrieveAPIView):
    """
    GET /api/brands/{slug}/
    Get brand detail with products
    """
    serializer_class = BrandDetailSerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'
    
    def get_queryset(self):
        """Get active brands with active products"""
        return Brand.objects.filter(is_active=True).prefetch_related(
            'products__images',
            'products__category',
            'products__variants'
        )


class SearchView(APIView):
    """
    GET /api/search/
    Search across products, categories, and brands
    
    Query Parameters:
        - q (required): Search text
        - type (required): Filter by type - 'product', 'brand', or 'category'
        - limit (optional): Limit results (default: 10)
    
    Response:
        Returns a list of search results with title, slug, url, and type
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        search_query = request.query_params.get('q', '').strip()
        search_type = request.query_params.get('type', '').lower()
        limit = request.query_params.get('limit', 10)
        
        # Validate search query
        if not search_query:
            return bad_request_response(
                message="Search query 'q' is required",
                errors={"q": ["This field is required"]}
            )
        
        # Validate search type
        valid_types = ['product', 'brand', 'category']
        if not search_type:
            return bad_request_response(
                message="Search type 'type' is required",
                errors={"type": [f"This field is required. Must be one of: {', '.join(valid_types)}"]}
            )
        
        if search_type not in valid_types:
            return bad_request_response(
                message=f"Invalid type. Must be one of: {', '.join(valid_types)}",
                errors={"type": [f"Invalid type. Must be one of: {', '.join(valid_types)}"]}
            )
        
        # Validate limit
        try:
            limit = int(limit)
            if limit < 1:
                limit = 10
            elif limit > 50:
                limit = 50
        except (ValueError, TypeError):
            limit = 10
        
        results = []
        
        # Helper to build absolute URL for images
        def build_image_url(image_field):
            if image_field:
                return request.build_absolute_uri(image_field.url)
            return None
        
        # Search products
        if search_type == 'product':
            products = Product.objects.filter(
                is_active=True,
            ).filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query)
            ).prefetch_related('images')[:limit]
            
            for p in products:
                # Get primary image (position=0)
                image_url = None
                for img in p.images.all():
                    if img.position == 0 and img.image:
                        image_url = build_image_url(img.image)
                        break
                
                results.append({
                    'title': p.title,
                    'slug': p.slug,
                    'image': image_url,
                    'url': f"products/{p.slug}",
                    'type': 'product'
                })
        
        # Search categories
        elif search_type == 'category':
            categories = Category.objects.filter(
                is_active=True,
            ).filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query)
            )[:limit]
            
            for c in categories:
                results.append({
                    'title': c.name,
                    'slug': c.slug,
                    'image': build_image_url(c.image),
                    'url': f"products?category={c.slug}",
                    'type': 'category'
                })
        
        # Search brands
        elif search_type == 'brand':
            brands = Brand.objects.filter(
                is_active=True,
            ).filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query)
            )[:limit]
            
            for b in brands:
                results.append({
                    'title': b.name,
                    'slug': b.slug,
                    'image': build_image_url(b.logo),
                    'url': f"products?brand={b.slug}",
                    'type': 'brand'
                })
        
        return success_response(
            data={
                'query': search_query,
                'type': search_type,
                'count': len(results),
                'results': results
            },
            message="Search results retrieved successfully"
        )
