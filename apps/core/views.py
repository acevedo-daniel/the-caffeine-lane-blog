from django.shortcuts import render
from apps.posts.models import Post, Category

def landing(request):
    return render(request, 'core/landing.html')

def home(request):
    banner_posts = Post.objects.filter(status='published').order_by('-created_at')[:5]

    new_builds = Post.objects.filter(
        status='published',
        category__name='Builds'
    ).order_by('-created_at')[:8]

    new_guides = Post.objects.filter(
        status='published',
        category__name='Guides'
    ).order_by('-created_at')[:5]

    new_reviews = Post.objects.filter(
        status='published',
        category__name='Reviews'
    ).order_by('-created_at')[:5]

    total_posts = Post.objects.filter(status='published').count()
    categories = Category.objects.all()

    context = {
        'banner_posts': banner_posts,
        'new_builds': new_builds,
        'new_guides': new_guides,
        'new_reviews': new_reviews,
        'total_posts': total_posts,
        'categories': categories,
    }

    return render(request, 'core/home.html', context)
