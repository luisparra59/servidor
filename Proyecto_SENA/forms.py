from django import forms #esta es la funcion para que django lea los formularios
from django.contrib.auth.forms import UserCreationForm #es la funcion base de django para crear usuarios y registrarlos
from django.contrib.auth.models import User #es el modelo predeterminado que trae django
from .models import UserProfile #este es un modelo personalizado para informacion adicional del usuario7
from .models import Contact


class CustomUserCreationForm(UserCreationForm): #clase que hereda de la funcion que importamos antes para crear los formularios en django, es para campos adicionales 
    email = forms.EmailField(required=True)
    numero = forms.CharField(max_length=15) #en estos tres declaro los campos con el tipo de datos que es, y con los caracteres maximos que puede ingresar el usuario
    direccion = forms.CharField(max_length=200)

    class Meta: #con esta clase especificamos que modelo vamos a usar, en este caso es User
        model = User #esto indica que estoy trabajando ene l modelo de usuario
        fields = ("username", "email", "password1", "password2") #especifico que campso se muestran segun el value de los inputs y que estos se guardaran

    def save(self, commit=True): #definimos una funcion save que primero guarde al usuario sin ningun comentario, commit crea un objeto usuario sin guardarlo en la base de datos
        user = super().save(commit=False)  #Permite modificar el objeto antes de guardarlo
        user.email = self.cleaned_data["email"] #le asignamos su correo
        if commit: #usamos el ciclo if para decirle que si se permite guardar el usuario, entonces guarde y cree un perfil, luego retorneme el usuaro creado
            user.save()
            # Crear el perfil de usuario
            UserProfile.objects.create(
                user=user,
                numero=self.cleaned_data.get('numero'), #se crea un perfin con telefono y direccion
                direccion=self.cleaned_data.get('direccion')
            )
        return user

class ContactForm(forms.ModelForm): #clase que hereda de la funcion para crear formularios en django
    class Meta: #con esta clase especificamos que modelo vamos a usar, en este caso es Contact
        model = Contact #esto indica que estoy trabajando en el modelo de Contact
        fields = ('nombre', 'email', 'telefono', 'mensaje') #especifico que campos se muestran segun el value de los inputs y que estos se guardaran

from .models import Order

class PasarelaForm(forms.ModelForm):
    nombre = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Tu nombre aquí...'
        })
    )
    
    apellido = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Tu apellido aquí...'
        })
    )
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control registrado',
        })
    )
    
    telefono = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={
            'class': 'form-control registrado',
        })
    )
    
    direccion = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control registrado',
        })
    )
    
    municipios = [
        ('', 'Selecciona un municipio'),
        ('Agrado', 'Agrado'),
        ('Pital', 'Pital'),
    ]
    
    municipio = forms.ChoiceField(
        choices=municipios,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    metodos_pago = [
        ('contra-entrega', 'Pago contra entrega'),
        ('nequi', 'Nequi'),
        ('daviplata', 'DaviPlata'),
    ]
    
    metodo_pago = forms.ChoiceField(
        choices=metodos_pago,
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input'
        })
    )

    class Meta:
        model = Order
        fields = ['nombre', 'apellido', 'email', 'telefono', 'direccion', 'municipio', 'metodo_pago']

    def clean(self):
        cleaned_data = super().clean()
        metodo_pago = cleaned_data.get('metodo_pago')
        
        # Validaciones específicas según el método de pago
        if metodo_pago in ['nequi', 'daviplata']:
            telefono = cleaned_data.get('telefono')
            if not telefono:
                self.add_error('telefono', 'El número de teléfono es obligatorio para pagos por Nequi o DaviPlata')
        
        return cleaned_data