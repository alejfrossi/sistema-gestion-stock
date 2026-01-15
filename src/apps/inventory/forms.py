from django import forms
from .models import Product, StockMovement

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['sku', 'name', 'category', 'quantity', 'price']
        
        # Estilos de Bootstrap (clase 'form-control') para cada input
        widgets = {
            'sku': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: PROD-001'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Monitor 24"'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        # Etiquetas personalizadas
        labels = {
            'sku': 'Código SKU',
            'name': 'Nombre del Producto',
            'category': 'Categoría',
            'quantity': 'Cantidad en Stock',
            'price': 'Precio Unitario'
        }

class StockMovementForm(forms.ModelForm):
    class Meta:
        model = StockMovement
        fields = ['product', 'movement_type', 'quantity', 'reason']
        
        widgets = {
            'product': forms.Select(attrs={'class': 'form-select'}),
            'movement_type': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'reason': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Recepción de pedido #123'}),
        }
        labels = {
            'product': 'Producto',
            'movement_type': 'Tipo de Movimiento',
            'quantity': 'Cantidad',
            'reason': 'Motivo'
        }