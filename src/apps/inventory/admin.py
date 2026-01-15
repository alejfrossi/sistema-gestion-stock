from django.contrib import admin
from .models import Category, Product , StockMovement

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description') # Columnas a mostrar en la lista
    search_fields = ('name',) # Barra de búsqueda

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'quantity', 'created_at')
    list_filter = ('category',) # Filtro lateral por categoría
    search_fields = ('name',) # Buscador por nombre

@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ('product', 'movement_type', 'quantity', 'reason', 'user', 'created_at')
    list_filter = ('movement_type', 'created_at', 'user')
    search_fields = ('product__name', 'reason')