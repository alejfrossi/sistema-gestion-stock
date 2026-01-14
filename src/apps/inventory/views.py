from django.shortcuts import render
from .models import Product

def product_list(request):
    # 1. Consultar a la DB (SELECT * FROM product)
    products = Product.objects.all()
    
    # 2. Contexto: El "paquete" de datos que enviamos al HTML
    context = {
        'products': products
    }
    
    # 3. Renderizar: Unir el HTML con los datos
    return render(request, 'inventory/product_list.html', context)