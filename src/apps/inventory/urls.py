from django.urls import path
from . import views

urlpatterns = [
    # Ruta vacía '' significa la raíz de esta app
    path('', views.product_list, name='product_list'),
    path('nuevo/', views.product_create, name='product_create'),
    path('editar/<int:pk>/', views.product_update, name='product_update'),
    path('eliminar/<int:pk>/', views.product_delete, name='product_delete'),
    path('movimientos/nuevo/', views.stock_movement_create, name='stock_movement_create'),
    path('reporte/pdf/', views.generate_report, name='generate_report'),
]