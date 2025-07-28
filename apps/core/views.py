# the-caffeine-lane-blog/apps/core/views.py

from django.shortcuts import render
# Importa Post desde la app 'posts', no desde '.models' de 'core'
from apps.posts.models import Post # ¡Corrección importante!

def landing(request):
    """
    Vista para la página de aterrizaje.
    Renderiza la plantilla 'core/landing.html'.
    """
    return render(request, 'core/landing.html')

def home(request):
    """
    Vista para la página de inicio que muestra los últimos posts.
    """
    # Consulta los posts, ordenados por fecha de creación descendente.
    # Usamos 'posts' (plural) para una colección, por claridad.
    posts = Post.objects.all().order_by('-created_at')
    # Pasa el QuerySet de posts a la plantilla bajo la clave 'posts'.
    return render(request, 'core/home.html', {'posts': posts}) # ¡Corrección de nombre de variable!
