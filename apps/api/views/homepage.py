"""
API Views for homepage content
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from core.models import Banner, FeaturedSection
from catalog.models import Category, Brand
from api.serializers import (
    BannerSerializer, 
    FeaturedSectionSerializer,
    HomepageCategorySerializer,
    HomepageBrandSerializer,
    CategoryWithProductsSerializer
)
from api.utils import success_response


class HomepageView(APIView):
    """
    GET /api/homepage/
    Get homepage data (banners, featured sections, categories, and brands)
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Get active banners, featured sections, categories, brands, and category products"""
        # Get active banners that are currently active (considering date ranges)
        banners = Banner.objects.filter(is_active=True).select_related('link_product')
        active_banners = [banner for banner in banners if banner.is_currently_active()]
        
        # Get active featured sections
        featured_sections = FeaturedSection.objects.filter(
            is_active=True
        ).prefetch_related('products')
        
        # Get active categories (limit to top 10 or all if needed)
        categories = Category.objects.filter(
            is_active=True
        ).prefetch_related('products')[:20]
        
        # Get active brands (limit to featured brands or all)
        brands = Brand.objects.filter(
            is_active=True
        ).prefetch_related('products')[:20]
        
        # Get child categories with their products (categories that have a parent)
        # Limit to 3 child categories that have products
        child_categories = Category.objects.filter(
            is_active=True,
            parent__isnull=False  # Only child categories (has a parent)
        ).prefetch_related(
            'products',
            'products__images'
        ).order_by('display_order', 'name')
        
        # Filter to only include categories that have active products
        child_categories_with_products = [
            cat for cat in child_categories 
            if cat.products.filter(is_active=True).exists()
        ][:3]  # Limit to 3 categories
        
        data = {
            'banners': BannerSerializer(
                active_banners,
                many=True,
                context={'request': request}
            ).data,
            'featured_sections': FeaturedSectionSerializer(
                featured_sections,
                many=True,
                context={'request': request}
            ).data,
            'categories': HomepageCategorySerializer(
                categories,
                many=True,
                context={'request': request}
            ).data,
            'brands': HomepageBrandSerializer(
                brands,
                many=True,
                context={'request': request}
            ).data,
            'category_products': CategoryWithProductsSerializer(
                child_categories_with_products,
                many=True,
                context={'request': request}
            ).data
        }
        
        return success_response(
            data=data,
            message="Homepage data retrieved successfully"
        )
