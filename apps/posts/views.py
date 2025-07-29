from django.shortcuts import render
from apps.posts.models import Post, Category

def post_list(request):
    new_posts = Post.objects.filter(status='published').order_by('-created_at')[:4]

    harley_posts = Post.objects.filter(status='published', category__name='Harley Davidson').order_by('-created_at')[:6]

    build_posts = Post.objects.filter(status='published', category__name='Builds').order_by('-created_at')[:3]

    news_posts = Post.objects.filter(status='published', category__name='News').order_by('-created_at')[:3]

    context = {
        'new_posts': new_posts,
        'harley_posts': harley_posts,
        'build_posts': build_posts,
        'news_posts': news_posts,
    }

    return render(request, 'posts/post_list.html', context)   