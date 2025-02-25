from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import FormularioRegistroUsuario, FormularioContacto, FormularioPasarela
from .models import (
    Producto, Inventario, Pedido, ProductosPedido,
    HistorialPedidos, Contacto
)
from django.http import JsonResponse
from decimal import Decimal
import json
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from django.core.paginator import Paginator
from django.contrib.staticfiles import finders
import os

def inicio(request):
    """Vista para la página de inicio"""
    return render(request, 'inicio.html')

def galeria(request):
    """Vista para la galería de imágenes"""
    return render(request, 'galeria.html')

def perfil(request):
    """Vista para el perfil de usuario"""
    return render(request, 'perfil.html')

def catalogo(request):
    """Vista para el catálogo de productos"""
    return render(request, 'catalogo.html')

def carrito(request):
    """Vista para el carrito de compras"""
    return render(request, 'carrito.html')

def manual(request):
    """Vista para el carrito el manual de usuario"""
    return render(request, 'manual.html')

def logout_perfil(request):
    """Función para cerrar sesión"""
    logout(request)
    return redirect('inicio')

def register(request):
    """
    Vista para el registro de nuevos usuarios.
    Procesa el formulario de registro y crea nuevas cuentas.
    """
    if request.method == "POST":
        form = FormularioRegistroUsuario(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Registro exitoso, Por favor inicia sesión")
            return redirect('login')
        else:
            for field in form.errors:
                for error in form[field].errors:
                    messages.error(request, f"{field}: {error}")
    return render(request, 'register.html', {'register_mode': True})

def login(request):
    """
    Vista para el inicio de sesión.
    Autentica a los usuarios y crea su sesión.
    """
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                auth_login(request, user)
                return redirect('catalogo')
            else:
                messages.error(request, "Usuario o contraseña incorrectos")
        else:
            messages.error(request, "Usuario o contraseña incorrectos")
    return render(request, 'login.html', {'register_mode': False})

@login_required(login_url='login')
def perfil(request):
    """
    Vista para gestionar el perfil del usuario.
    Permite cambiar contraseña y eliminar cuenta.
    """
    if request.method == 'POST':
        if 'delete_account' in request.POST:
            request.user.delete()
            messages.success(request, "Cuenta eliminada exitosamente")
            return redirect('inicio')
        elif 'change_password' in request.POST:
            password_form = PasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                messages.success(request, 'Contraseña actualizada exitosamente')
                logout(request)
                return redirect('login')
            else:
                for error in password_form.errors.values():
                    messages.error(request, error[0])
    else:
        password_form = PasswordChangeForm(request.user)

    try:
        profile = request.user.perfilusuario
        context = {
            'user': request.user,
            'profile': profile,
            'password_form': password_form
        }
        return render(request, 'perfil.html', context)
    except AttributeError:
        return render(request, 'perfil.html', {'password_form': password_form})

def get_products(request):
    productos = Producto.objects.filter(disponible=True).values(
        'id', 'nombre', 'descripcion', 'precio', 
        'categoria', 'imagen'
    )
    
    productos_list = list(productos)
    
    for producto in productos_list:
        try:
            inventario = Inventario.objects.get(producto_id=producto['id'])
            producto['available_units'] = inventario.unidades_totales 
        except Inventario.DoesNotExist:
            producto['available_units'] = 0
    
    return JsonResponse(productos_list, safe=False)

def contact(request):
    """
    Vista para procesar el formulario de contacto.
    Guarda los mensajes de contacto en la base de datos.
    """
    if request.method == 'POST':
        form = FormularioContacto(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Mensaje enviado")
            return redirect('contact')
        else:
            for field in form.errors:
                for error in form[field].errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = FormularioContacto()
    return render(request, 'inicio.html', {'form': form})

def get_datos(user):
    """
    Función auxiliar para obtener datos del usuario.
    """
    if hasattr(user, 'perfilusuario'):
        return {
            'nombre': user.first_name,
            'apellido': user.last_name,
            'email': user.email,
            'telefono': user.perfilusuario.numero,
            'direccion': user.perfilusuario.direccion
        }
    return {}

@login_required
def usuario_info(request):
    """
    Vista para obtener información del usuario.
    Retorna un JSON con los datos del perfil.
    """
    user = request.user
    user_profile = user.perfilusuario
    
    return JsonResponse({
        'usuario': {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'numero': user_profile.numero,
            'direccion': user_profile.direccion
        }
    })

@login_required
def pasarela(request):
    """
    Vista para procesar el pago y crear pedidos.
    Maneja la creación de pedidos y sus productos asociados.
    """
    if request.method == 'POST':
        form = FormularioPasarela(request.POST)
        if form.is_valid():
            try:
                carrito_data = request.POST.get('carrito_data')
                if not carrito_data:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'El carrito está vacío'
                    })

                carrito = json.loads(carrito_data)
                if not carrito:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'El carrito está vacío'
                    })

                # Crear el pedido
                pedido = form.save(commit=False)
                pedido.usuario = request.user
                pedido.subtotal = Decimal(str(sum(Decimal(str(item['precio'])) * int(item['cantidad']) for item in carrito)))
                pedido.costo_envio = Decimal('3000')
                pedido.total = pedido.subtotal + pedido.costo_envio
                pedido.save()

                # Guardar productos del pedido
                for item in carrito:
                    producto = Producto.objects.get(id=item['id'])
                    cantidad = int(item['cantidad'])
                    try:
                        inventario = Inventario.objects.get(producto=producto)
                        if inventario.disminuir_stock(cantidad):
                            ProductosPedido.objects.create(
                                pedido=pedido,
                                producto=producto,
                                cantidad=cantidad,
                                precio_unitario=Decimal(str(item['precio'])),
                                subtotal=Decimal(str(item['precio'])) * cantidad
                            )
                        else:
                            return JsonResponse({
                                'status': 'error',
                                'message': f'No hay suficiente stock para {producto.nombre}'
                            })
                    except Inventario.DoesNotExist:
                        return JsonResponse({
                            'status': 'error',
                            'message': f'No hay inventario para {producto.nombre}'
                        })
                
                # Crear registro en el historial
                HistorialPedidos.objects.create(
                    usuario=request.user,
                    numero_pedido=f"#{pedido.id}",
                    numero_productos=sum(int(item['cantidad']) for item in carrito),
                    compra_total=pedido.total
                )

                return JsonResponse({
                    'status': 'success',
                    'message': 'Pedido creado, espere confirmación por correo',
                    'redirect': 'historial/'
                })
            
            except Producto.DoesNotExist:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Uno o más productos no existen en la base de datos'
                })
        else:
            return JsonResponse({
                'status': 'error',
                'errors': form.errors
            })

    form = FormularioPasarela(initial=get_datos(request.user))
    return render(request, 'pasarela.html', {
        'form': form
    })

def MessagePasarela(request):
    """
    Vista para enviar correos de confirmación de pedido.
    Procesa los datos del pedido y envía un correo al cliente.
    """
    if request.method == "POST":
        try:
            nombre = request.POST.get('nombre')
            apellido = request.POST.get('apellido')
            email = request.POST.get('email')
            telefono = request.POST.get('telefono')
            direccion = request.POST.get('direccion')
            metodo_pago = request.POST.get('metodo_pago')
            carrito_data = request.POST.get('carrito_data')
            
            productos = json.loads(carrito_data) if carrito_data else []
            
            for producto in productos:
                producto['subtotal'] = float(producto['precio']) * int(producto['cantidad'])
            
            subtotal = sum(float(item['precio']) * int(item['cantidad']) for item in productos)
            envio = 3000
            total = subtotal + envio
            
            template = render_to_string('email_template.html', {
                'nombre': nombre,
                'apellido': apellido,
                'email': email,
                'telefono': telefono,
                'direccion': direccion,
                'metodo_pago': metodo_pago,
                'productos': productos,
                'subtotal': f"{subtotal:,.0f}",
                'envio': f"{envio:,.0f}",
                'total': f"{total:,.0f}"
            })
            
            email_message = EmailMessage(
                'Confirmación de pedido - Tienda Luigui',
                template,
                settings.EMAIL_HOST_USER,
                [email]
            )

            if metodo_pago == 'nequi':
                qr_path = finders.find('images/QR-Nequi.jpg')
                if qr_path:
                    with open(qr_path, 'rb') as f:
                        email_message.attach('qr_nequi.jpg', f.read(), 'image/png')
            elif metodo_pago == 'daviplata':
                qr_path = finders.find('images/QR-DaviPlata.jpg')
                if qr_path:
                    with open(qr_path, 'rb') as f:
                        email_message.attach('qr_daviplata.jpg', f.read(), 'image/webp')
            
            email_message.content_subtype = "html"
            email_message.send()
            
            return JsonResponse({
                'status': 'success',
                'message': 'Pedido confirmado. Revisa tu correo.',
                'redirect': '/catalogo/'
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Error al procesar el pedido: {str(e)}'
            })

@login_required
def history(request):
    """
    Vista para mostrar el historial de pedidos del usuario.
    Incluye paginación para mejor navegación.
    """
    pedidos = HistorialPedidos.objects.filter(usuario=request.user).order_by('-fecha_compra')
    paginator = Paginator(pedidos, 10)
    
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'historial.html', {'page_obj': page_obj})

from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str

def restablecer(request):
    if request.method == "POST":
        email = request.POST.get("email")
        user = User.objects.filter(email=email).first()
        if user:
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            enlace = request.build_absolute_uri(f"/cambiar_contrasena/{uid}/{token}/")
            send_mail(
                'Restablecer contraseña',
                f'Haz clic en el siguiente en enlace para restablecer tu contraseña {enlace}',
                'TiendaLuigui1@gmail.com',
                [email], 
                fail_silently=False
            )
            messages.success(request, "Se ah enviado un enlace de restablecimiento de contraseña a su correo")
            return redirect('login')
        else:
            messages.success(request, "No se encontro algun usuario registrado con ese correo")
        return redirect('restablecer')
    return render(request, 'email_restablecer.html')

def cambiar_contrasena(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))  
        user = User.objects.get(pk=uid) 
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user and default_token_generator.check_token(user, token):
        if request.method == "POST":
            nueva_contrasena = request.POST.get("password")
            
            if not nueva_contrasena:
                messages.error(request, "La contraseña no puede estar vacía")
                return render(request, "email_contrasena.html")
                
            
            user.set_password(nueva_contrasena)
            user.save()
            
            return redirect('confirmacion_contrasena')
        
        return render(request, "email_contrasena.html")
    return redirect("login")

def confirmacion_contrasena(request):
    return render(request, "cambio_contrasena.html")