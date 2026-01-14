from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'quantity', 'price']
        
        # Estilos de Bootstrap (clase 'form-control') para cada input
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Monitor 24"'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        # Etiquetas personalizadas
        labels = {
            'name': 'Nombre del Producto',
            'category': 'Categoría',
            'quantity': 'Cantidad en Stock',
            'price': 'Precio Unitario'
        }