from django.shortcuts import render, redirect, get_object_or_404
from .models import Product
from .forms import ProductForm

def product_list(request):
    products = Product.objects.all() # 1. Consultar a la DB (SELECT * FROM product)
    context = { 'products': products } # 2. Contexto: El "paquete" de datos que enviamos al HTML
    return render(request, 'inventory/product_list.html', context) # 3. Renderizar: Unir el HTML con los datos

def product_create(request):
    if request.method == 'POST':
        # Si es POST (el usuario envía datos), se rellena el formulario con ellos
        form = ProductForm(request.POST)
        if form.is_valid():
            # Guardar en DB
            form.save()
            # Redirigir al listado para ver el nuevo producto
            return redirect('product_list')
    else:
        # Si es GET (el usuario pide la página), creamos un formulario vacío
        form = ProductForm()

    return render(request, 'inventory/product_form.html', {'form': form})

def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)

    return render(request, 'inventory/product_form.html', {'form': form, 'product': product})

def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        # Solo eliminamos si la petición es POST (seguridad)
        product.delete()
        return redirect('product_list')

    # Si es GET, mostramos la página de confirmación
    return render(request, 'inventory/product_confirm_delete.html', {'product': product})