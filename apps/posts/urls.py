from django.urls import path
from . import views

urlpatterns = [
    path('', views.post_list, name='post_list'),
    # Aquí irán más rutas de posts en el futuro
]