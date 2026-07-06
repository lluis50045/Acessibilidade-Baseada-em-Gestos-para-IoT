from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from autenticao import views as auth_views
from django.conf.urls import handler404
from django.shortcuts import render

from dashboard import views as dashboard_views

def custom_404_view(request, exception):
    return render(request, '404.html', status=404)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', auth_views.home, name='login'),
    path('callback/', auth_views.amazon_callback, name='amazon_callback'),
    path('home/', dashboard_views.home,  name='dashboard'),
    path('logout/', dashboard_views.logout_view, name='logout'),
    path('registrar-gesto/', dashboard_views.RegistrarGestoView.as_view(), name='registrar_gesto'),
    path('deletar-gesto/', dashboard_views.deletarGesto.as_view(), name='deletar_gesto'),
    path('', auth_views.principal, name='principal'),
    path('api/get-config/', dashboard_views.get_gestos_por_usuario, name='get_config'),
]
handler404 = custom_404_view

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

