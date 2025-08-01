from django.shortcuts import render
from apps.posts.models import Post, Category

def landing(request):
    return render(request, 'core/landing.html')

def home(request):
    # Post destacado para el banner
    banner_posts = Post.objects.filter(status='published').order_by('-created_at')[:5]

    # Secciones por categoría
    new_builds = Post.objects.filter(
        status='published',
        category__name='Builds'
    ).order_by('-created_at')[:6]

    harley_davidson_posts = Post.objects.filter(
        status='published',
        category__name='Harley Davidson'
    ).order_by('-created_at')[:3]

    latest_news_posts = Post.objects.filter(
        status='published',
        category__name='News'
    ).order_by('-created_at')[:3]

    # Estadísticas para mostrar
    total_posts = Post.objects.filter(status='published').count()
    categories = Category.objects.all()

    context = {
        'banner_posts': banner_posts, # ¡Corregido aquí!
        'new_builds': new_builds,
        'harley_davidson_posts': harley_davidson_posts,
        'latest_news_posts': latest_news_posts,
        'total_posts': total_posts,
        'categories': categories,
    }

    return render(request, 'core/home.html', context)
