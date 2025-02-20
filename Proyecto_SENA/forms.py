from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import PerfilUsuario, Contacto, Pedido

class FormularioRegistroUsuario(UserCreationForm):
    """
    Formulario personalizado para el registro de usuarios.
    Extiende el formulario base de Django agregando campos adicionales.
    """
    email = forms.EmailField(required=True)
    numero = forms.CharField(max_length=15)
    direccion = forms.CharField(max_length=200)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.email = self.cleaned_data["email"]
        if commit:
            usuario.save()
            PerfilUsuario.objects.create(
                usuario=usuario,
                numero=self.cleaned_data.get('numero'),
                direccion=self.cleaned_data.get('direccion')
            )
        return usuario

class FormularioContacto(forms.ModelForm):
    """
    Formulario para el envío de mensajes de contacto.
    """
    class Meta:
        model = Contacto
        fields = ('nombre', 'email', 'telefono', 'mensaje')

class FormularioPasarela(forms.ModelForm):
    """
    Formulario para la pasarela de pago.
    """
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
    
    MUNICIPIOS = [
        ('', 'Selecciona un municipio'),
        ('Agrado', 'Agrado'),
        ('Pital', 'Pital'),
    ]
    
    municipio = forms.ChoiceField(
        choices=MUNICIPIOS,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    metodo_pago = forms.ChoiceField(
        choices=Pedido.METODOS_PAGO,
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input'
        })
    )

    class Meta:
        model = Pedido
        fields = ['nombre', 'apellido', 'email', 'telefono', 'direccion', 'municipio', 'metodo_pago']

    def clean(self):
        datos_limpios = super().clean()
        metodo_pago = datos_limpios.get('metodo_pago')
        
        if metodo_pago in ['nequi', 'daviplata']:
            telefono = datos_limpios.get('telefono')
            if not telefono:
                self.add_error('telefono', 'El número de teléfono es obligatorio para pagos por Nequi o DaviPlata')
        return datos_limpios