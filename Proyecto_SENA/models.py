from django.db import models #importamos modelos de bases de datos de django
from django.contrib.auth.models import User#importamos modelos de usuario predeterminados, este modelo trae campos basicos como el nombre de usuario, apellidos, contraseñas, etc

class UserProfile(models.Model): #Define el modelo UserProfile que extiende la información del usuario
    user = models.OneToOneField(User, on_delete=models.CASCADE) #creamos una relacion de uno a uno con el modelo usuario y despues si se elimina el usuario, se elimina el perfil. Luego user permite agregar campos extra que no vienen por defecto en la funcion user que importe antes
    
    numero = models.CharField(max_length=15)
    direccion = models.CharField(max_length=200)

def __str__(self):
        return self.user.username


class Contact(models.Model):
    nombre = models.CharField(max_length=60)
    email = models.EmailField()
    telefono = models.CharField(max_length=11)
    mensaje = models.TextField()

    def __str__(self):
        return self.nombre

class Products(models.Model):
    CATEGORIES = [
        ('aseo', 'Aseo'),
        ('comestibles', 'Comestibles'),
        ('canastafamiliar', 'Canasta Familiar'),
        ('papeleria', 'Papelería'),
    ]

    nombre = models.CharField(max_length=200, verbose_name="Nombre")
    descripcion = models.TextField(verbose_name="Descripción")
    precio = models.DecimalField(max_digits=10, decimal_places=0, verbose_name="Precio")
    categoria = models.CharField(max_length=20, choices=CATEGORIES, verbose_name="Categoría")
    imagen = models.ImageField(upload_to='products/', verbose_name="Imagen")
    disponible = models.BooleanField(default=True, verbose_name="Disponible")

    def __str__(self):
        return self.nombre

class CarShopping(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    productos = models.ForeignKey(Products, on_delete=models.CASCADE)
    cantidad = models.IntegerField(default=1)

    def __str__(self):
        return self.user.username + self.producto.nombre    

class Order(models.Model):
    metodos_pago = [
        ('contra-entrega', 'Pago contra entrega'),
        ('nequi', 'Nequi'),
        ('daviplata', 'DaviPlata'),
    ]
    
    estado_compra = [
        ('pendiente', 'Pendiente'),
        ('confirmado', 'Confirmado'),
        ('en_proceso', 'En Proceso'),
        ('enviado', 'Enviado'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    nombre = models.CharField(max_length=200)
    apellido = models.CharField(max_length=200)
    direccion = models.CharField(max_length=200)
    telefono = models.CharField(max_length=15)
    email = models.EmailField()
    municipio = models.CharField(max_length=100)
    metodo_pago = models.CharField(max_length=20, choices=metodos_pago)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    costo_envio = models.DecimalField(max_digits=10, decimal_places=2, default=3000)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=20, choices=estado_compra, default='pendiente')

    def __str__(self):
        return f"Orden #{self.id} - {self.user.username}"

class OrderProducts(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    producto = models.ForeignKey('Products', on_delete=models.CASCADE)
    cantidad = models.IntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        self.subtotal = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.cantidad}x {self.producto.nombre} en Orden #{self.order.id}"
    
class OrderHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_compra = models.DateTimeField(auto_now_add=True)  
    numero_productos = models.IntegerField()  
    compra_total = models.DecimalField(max_digits=10, decimal_places=2)  
    numero_orden = models.CharField(max_length=10)  

    def __str__(self):
        return f"Orden #{self.numero_orden} - {self.user.username}"