import requests
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from .models import Product, StockMovement
from .forms import ProductForm, StockMovementForm

@login_required
def product_list(request):
    products = Product.objects.all()
    query = request.GET.get('q')
    
    if query:
        # Filtramos: El nombre contiene la query ó la categoría contiene la query
        products = products.filter(
            Q(name__icontains=query) | 
            Q(sku__icontains=query) |
            Q(category__name__icontains=query)
        )

    context = { 'products': products, 'search_query': query }
    return render(request, 'inventory/product_list.html', context)

@login_required
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

@login_required
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

@login_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        # Solo eliminamos si la petición es POST (seguridad)
        product.delete()
        return redirect('product_list')

    # Si es GET, mostramos la página de confirmación
    return render(request, 'inventory/product_confirm_delete.html', {'product': product})

@login_required
def stock_movement_create(request):
    if request.method == 'POST':
        form = StockMovementForm(request.POST)
        if form.is_valid():
            # No guardamos en DB todavía (commit=False)
            movement = form.save(commit=False)
            
            movement.user = request.user

            # Sí guardamos en DB (actualiza el stock)
            movement.save()
            
            return redirect('product_list')
    else:
        form = StockMovementForm()

    return render(request, 'inventory/stock_movement_form.html', {'form': form})

@login_required
def generate_report(request):
    # Obtener datos de la DB
    products = Product.objects.all()

    # Serializar datos (Convertir objetos Python a lista de diccionarios)
    data_payload = {
        "products": [
            {
                "name": p.name,
                "sku": p.sku if p.sku else "-",
                "quantity": p.quantity,
                "price": float(p.price)
            } for p in products
        ]
    }

    # Llamar al Microservicio
    try:
        response = requests.post("http://127.0.0.1:8001/generate-pdf/", json=data_payload)
        
        # Devolver el PDF al navegador
        if response.status_code == 200:
            django_response = HttpResponse(response.content, content_type='application/pdf')
            django_response['Content-Disposition'] = 'attachment; filename="reporte_stock.pdf"'
            return django_response
        else:
            return HttpResponse("Error en el microservicio", status=500)
            
    except requests.exceptions.ConnectionError:
        return HttpResponse("El servicio de PDF no está disponible", status=503)