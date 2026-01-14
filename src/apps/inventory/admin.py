from django.contrib import admin
from .models import Category, Product

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description') # Columnas a mostrar en la lista
    search_fields = ('name',) # Barra de búsqueda

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'quantity', 'created_at')
    list_filter = ('category',) # Filtro lateral por categoría
    search_fields = ('name',) # Buscador por nombre