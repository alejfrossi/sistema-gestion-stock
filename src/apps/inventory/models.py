from django.db import models
from django.contrib.auth.models import User

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
    
    @property
    def total_value(self):
        return self.price * self.quantity
    
# Movimiento de Stock
class StockMovement(models.Model):
    MOVEMENT_TYPES = (
        ('IN', 'Entrada'),
        ('OUT', 'Salida'),
    )

    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Producto")
    movement_type = models.CharField(max_length=3, choices=MOVEMENT_TYPES, verbose_name="Tipo")
    quantity = models.PositiveIntegerField(verbose_name="Cantidad")
    reason = models.CharField(max_length=200, verbose_name="Motivo", help_text="Ej: Compra, Venta, Devolución")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Usuario")

    class Meta:
        verbose_name = "Movimiento de Stock"
        verbose_name_plural = "Movimientos de Stock"
        ordering = ['-created_at'] # Los más recientes primero

    def __str__(self):
        return f"{self.get_movement_type_display()} de {self.quantity} - {self.product.name}"
    
    # El método save() para que actualice el producto automáticamente.
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs) # Guardamos el movimiento en la DB
        
        if self.movement_type == 'IN':
            self.product.quantity += self.quantity
        elif self.movement_type == 'OUT':
            self.product.quantity -= self.quantity
        
        self.product.save()