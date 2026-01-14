from django.urls import path
from . import views

urlpatterns = [
    # Ruta vacía '' significa la raíz de esta app
    path('', views.product_list, name='product_list'),
]