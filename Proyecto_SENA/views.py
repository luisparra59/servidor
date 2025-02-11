from django.shortcuts import render

# Create your views here.

def inicio(request):
    return render(request,'inicio.html')

def galeria(request):
    return render(request,'galeria.html')

def perfil(request):
    return render(request, 'perfil.html')

def catalogo(request):
    return render(request, 'catalogo.html')

def carrito(request):
    return render(request, 'carrito.html')




from django.shortcuts import render, redirect  
from django.contrib.auth import login as auth_login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm  
from django.contrib import messages  # importo los mensajes para mostrar errores o confirmaciones
from django.contrib.auth.decorators import login_required  # importo el decorador para proteger vistas
from .forms import CustomUserCreationForm  # importo mi formulario personalizado de registro



def logout_perfil(request):  # defino la funcion para cerrar sesion
    logout(request)  # cierro la sesion del usuario
    return redirect('inicio')  # redirecciono al inicio

def register(request):  # Función para manejar el registro de nuevos usuarios
    if request.method == "POST":  # Si el método es POST procesa el formulario
        form = CustomUserCreationForm(request.POST)  # Crea una instancia del formulario con los datos enviados
        if form.is_valid():  # Valida que los datos cumplan con los requisitos
            user = form.save()  # Guarda el nuevo usuario en la base de datos
            messages.success(request, "Registro exitoso, Por favor inicia sesión")  # Muestra mensaje de éxito
            return redirect('login')  # Redirecciona al login
        else:  # Si hay errores en el formulario
            for field in form.errors:  # Itera sobre cada campo con error
                for error in form[field].errors:  # Itera sobre cada error del campo
                    messages.error(request, f"{field}: {error}")  # Muestra mensaje de error específico
    return render(request, 'perfil.html', {'register_mode': True})  # Renderiza la plantilla de registro

def login(request):  # Función para manejar el inicio de sesión
    if request.method == "POST":  # Si el método es POST, procesa el formulario
        form = AuthenticationForm(request, data=request.POST)  # Crea instancia del formulario con los datos
        if form.is_valid():  # Valida las credenciales
            username = form.cleaned_data.get('username')  # Obtiene el nombre de usuario
            password = form.cleaned_data.get('password')  # Obtiene la contraseña
            user = authenticate(username=username, password=password)  # Autentica al usuario
            if user is not None:  # Si el usuario existe y las credenciales son correctas
                auth_login(request, user)  # Inicia la sesión del usuario
                return redirect('perfil')  # Redirecciona al perfil
            else:  # Si las credenciales son incorrectas
                messages.error(request, "Usuario o contraseña incorrectos")  # Muestra mensaje de error
        else:  # Si el formulario no es válido
            messages.error(request, "Usuario o contraseña incorrectos")  # Muestra mensaje de error
    return render(request, 'login.html', {'register_mode': False})  # Renderiza la plantilla de login

@login_required(login_url='login')  # Decorator que requiere inicio de sesión para acceder
def perfil(request):  # Función para manejar el perfil del usuario
    if request.method == 'POST':  # Si el método es POST, procesa el formulario
        if 'delete_account' in request.POST:  # Si se solicita eliminar la cuenta
            request.user.delete()  # Elimina el usuario
            messages.success(request, "Cuenta eliminada exitosamente")  # Muestra mensaje de confirmación
            return redirect('inicio')  # Redirecciona al inicio
        elif 'change_password' in request.POST:  # Si se solicita cambiar la contraseña
            password_form = PasswordChangeForm(request.user, request.POST)  # Crea instancia del formulario
            if password_form.is_valid():  # Valida los datos del formulario
                user = password_form.save()  # Guarda la nueva contraseña
                messages.success(request, 'Contraseña actualizada exitosamente')  # Muestra mensaje de éxito
                logout(request)  # Cierra la sesión del usuario
                return redirect('login')  # Redirecciona al login
            else:  # Si hay errores en el formulario
                for error in password_form.errors.values():  # Itera sobre los errores
                    messages.error(request, error[0])  # Muestra mensaje de error
    else:  # Si el método es GET
        password_form = PasswordChangeForm(request.user)  # Crea formulario vacío

    try:  # Intenta obtener el perfil del usuario
        profile = request.user.userprofile  # Obtiene el perfil del usuario
        context = {  # Crea el contexto con los datos necesarios
            'user': request.user,
            'profile': profile,
            'password_form': password_form
        }
        return render(request, 'perfil.html', context)  # Renderiza la plantilla con el contexto
    except AttributeError:  # Si no existe el perfil
        return render(request, 'perfil.html', {'password_form': password_form})  # Renderiza sin datos de perfil
    

from django.http import JsonResponse
from .models import Products

def get_products(request): # Función para obtener los productos disponibles
    products = Products.objects.filter(disponible=True).values( # Filtra los productos disponibles
        'id', 'nombre', 'descripcion', 'precio', 
        'categoria', 'imagen'
    )
    print("Productos encontrados:", list(products)) # Imprime los productos encontrados
    return JsonResponse(list(products), safe=False) # Retorna los productos en formato JSON



from .forms import ContactForm
def contact(request):  # Función para manejar el formulario de contacto
    if request.method == 'POST':  # Si el método es POST, procesa el formulario
        form = ContactForm(request.POST)  # Crea instancia del formulario con los datos
        if form.is_valid():  # Valida los datos del formulario
            form.save()  # Guarda los datos en la base de datos
            messages.success(request, "Mensaje enviado")  # Muestra mensaje de éxito
            return redirect('contact')  # Redirecciona a la misma página
        else:  # Si hay errores en el formulario
            for field in form.errors:  # Itera sobre cada campo con error
                for error in form[field].errors:  # Itera sobre cada error del campo
                    messages.error(request, f"{field}: {error}")  # Muestra mensaje de error específico
    else:  # Si el método es GET
        form = ContactForm()  # Crea formulario vacío
    return render(request, 'inicio.html', {'form': form})  # Renderiza la plantilla con el formulario


from decimal import Decimal
from .models import Order, OrderProducts
from .forms import PasarelaForm
import json

def get_datos(user):
    if hasattr(user, 'userprofile'):
        return {
            'nombre': user.first_name,
            'apellido': user.last_name,
            'email': user.email,
            'telefono': user.userprofile.numero,
            'direccion': user.userprofile.direccion
        }
    return {}

@login_required
def usuario_info(request):
    user = request.user
    user_profile = user.userprofile
    
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
    if request.method == 'POST':
        form = PasarelaForm(request.POST)
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

                # Crear la orden
                order = form.save(commit=False)
                order.user = request.user
                # Convertir todo a Decimal para evitar errores de tipo
                order.subtotal = Decimal(str(sum(Decimal(str(item['precio'])) * int(item['cantidad']) for item in carrito)))
                order.costo_envio = Decimal('3000')
                order.total = order.subtotal + order.costo_envio
                order.save()

                # Guardar productos del carrito
                for item in carrito:
                    producto = Products.objects.get(id=item['id'])
                    OrderProducts.objects.create(
                        order=order,
                        producto=producto,
                        cantidad=int(item['cantidad']),
                        precio_unitario=Decimal(str(item['precio'])),
                        subtotal=Decimal(str(item['precio'])) * int(item['cantidad'])
                    )
                
                # Crear registro en el historial
                OrderHistory.objects.create(
                    user=request.user,
                    numero_orden=f"#{order.id}",
                    numero_productos=sum(int(item['cantidad']) for item in carrito),
                    compra_total=order.total
                )

                return JsonResponse({
                    'status': 'success',
                    'message': 'Orden creada, espere confirmacion por correo',
                    'redirect_url': '/catalogo/'
                })

            except Products.DoesNotExist:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Uno o más productos no existen en la base de datos'
                })
            except json.JSONDecodeError:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Error al procesar el carrito'
                })
            except Exception as e:
                return JsonResponse({
                    'status': 'error',
                    'message': f'Error inesperado: {str(e)}'
                })
        else:
            return JsonResponse({
                'status': 'error',
                'errors': form.errors
            })

    # GET request
    form = PasarelaForm(initial=get_datos(request.user))
    return render(request, 'pasarela.html', {
        'form': form
    })


from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings

def MessagePasarela(request):
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
        
from .models import OrderHistory
from django.core.paginator import Paginator

@login_required
def history(request):
    orders = OrderHistory.objects.filter(user=request.user).order_by('-fecha_compra')
    paginator = Paginator(orders, 10)  # 10 órdenes por página
    
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'historial.html', {'page_obj': page_obj})