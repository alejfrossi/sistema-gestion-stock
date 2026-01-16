from rest_framework import serializers
from .models import Category, Product

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description']

class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 
            'sku', 
            'name', 
            'category',       # ID de la categoría (para escribir)
            'category_name',  # Nombre legible (para leer)
            'quantity', 
            'price', 
            'total_value'     # El campo calculado (@property) que se creo antes
        ]