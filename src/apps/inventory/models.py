from django.db import models

# Categoría
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Nombre")
    description = models.TextField(blank=True, null=True, verbose_name="Descripción")

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"

    def __str__(self):
        return self.name

# Producto
class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name="Nombre")

    # SKU único para identificar el producto.
    sku = models.CharField(max_length=50, unique=True, null=True, blank=True, verbose_name="Código SKU")
    
    # Relación: Un producto pertenece a una categoría.
    # on_delete=models.CASCADE significa: si borras la categoría 'Bebidas', 
    # se borran todos los productos que estén dentro (cuidado con esto en prod, pero útil ahora).
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="Categoría")
    
    # Stock: PositiveIntegerField para evitar stocks negativos mágicos.
    quantity = models.PositiveIntegerField(default=0, verbose_name="Cantidad")
    
    # Precio
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio")

    # Auditoría: Saber cuándo se creó o editó.
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"

    def __str__(self):
        return f"{self.name} (${self.price})"