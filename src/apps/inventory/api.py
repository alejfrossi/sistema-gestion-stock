from rest_framework import viewsets
from rest_framework.filters import SearchFilter
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    
    # Buscador nativo de la API (?search=...)
    filter_backends = [SearchFilter]
    search_fields = ['name', 'sku', 'category__name']