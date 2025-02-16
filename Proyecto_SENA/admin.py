from django.contrib import admin
from .models import (
    PerfilUsuario, Producto, Contacto, Pedido,
    ProductosPedido, Inventario
)

class AdminPerfilUsuario(admin.ModelAdmin):
    """
    Configuración de la interfaz administrativa para perfiles de usuario.
    """
    model = PerfilUsuario
    list_display = ('usuario', 'numero', 'direccion')

admin.site.register(PerfilUsuario, AdminPerfilUsuario)

@admin.register(Producto)
class AdminProducto(admin.ModelAdmin):
    """
    Configuración de la interfaz administrativa para productos.
    """
    list_display = ('nombre', 'categoria', 'precio', 'disponible', 'obtener_stock')
    search_fields = ('nombre', 'descripcion')
    
    def obtener_stock(self, obj):
        return obj.obtener_unidades_disponibles()
    obtener_stock.short_description = 'Stock Disponible'

class AdminMensajeContacto(admin.ModelAdmin):
    """
    Configuración de la interfaz administrativa para mensajes de contacto.
    """
    list_display = ('nombre', 'email', 'telefono', 'mensaje')

admin.site.register(Contacto, AdminMensajeContacto)

class ProductosPedidoInline(admin.TabularInline):
    """
    Configuración para mostrar productos dentro de un pedido en el admin.
    """
    model = ProductosPedido
    extra = 0
    readonly_fields = ('subtotal',)

@admin.register(Pedido)
class AdminPedido(admin.ModelAdmin):
    """
    Configuración de la interfaz administrativa para pedidos.
    """
    list_display = ['id', 'usuario', 'fecha_creacion', 'total', 'estado', 'metodo_pago']
    inlines = [ProductosPedidoInline]
    readonly_fields = ['fecha_creacion', 'subtotal', 'total']

@admin.register(Inventario)
class AdminInventario(admin.ModelAdmin):
    """
    Configuración de la interfaz administrativa para inventario.
    """
    list_display = ('producto', 'unidades_totales')
    search_fields = ('producto__nombre',)
