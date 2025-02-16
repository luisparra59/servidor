"""
URL configuration for Sitio project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from Proyecto_SENA import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.inicio,name='inicio'),
    path('galeria/',views.galeria,name='galeria'),
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('perfil/', views.perfil, name='perfil'),
    path('catalogo/', views.catalogo, name='catalogo'),
    path('logout/', views.logout_perfil, name='logout'),
    path('api/productos/', views.get_products, name='get_products'),
    path('contact/', views.contact, name='contact'),
    path('carrito/', views.carrito, name='carrito'),
    path('pasarela/', views.pasarela, name='pasarela'),
    path('api/usuario-info/', views.usuario_info, name='usuario_info'),
    path('message-pasarela/', views.MessagePasarela, name='MessagePasarela'),
    path('historial/', views.history, name='historial'),
    path('manual/', views.manual, name='manual'),
] 
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)




