from django.urls import path
<<<<<<< HEAD
from .views import views

urlpatterns = [
       # Aquí irán tus rutas de posts
       path('', views.post_list, name='post_list'),
       path('<slug:slug>/', views.post_detail, name='post_detail'),
=======
from . import views

urlpatterns = [
    path('', views.post_list, name='post_list'),
>>>>>>> origin/main
]