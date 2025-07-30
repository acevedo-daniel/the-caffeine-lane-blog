<<<<<<< HEAD
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Post, Category, Comment
from .forms import CommentForm

def create_and_save_comment(form, post, user):
    comment = form.save(commit=False)
    comment.post = post
    comment.user = user
    comment.save()

# Create your views here.
def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug, status='published')
    comments = post.comments.filter(is_active=True, parent=None)
    form = CommentForm()
    
    if request.method == 'POST' and request.user.is_authenticated:
        form = CommentForm(request.POST)
        if form.is_valid():
            create_and_save_comment(form, post, request.user)
            messages.success(request, '¡Comentario agregado exitosamente!')
            return redirect('post_detail', slug=post.slug)
    context = {
        'post': post, 
        'comments': comments, 
        'form': form
    }
    return render(request, 'posts/post_detail.html', context)

# Actualizar post_list existente
def post_list(request):
    new_posts = Post.objects.filter(status='published').order_by('-created_at')[:4]
    harley_posts = Post.objects.filter(status='published', category__name='Harley Davidson').order_by('-created_at')[:6]
    build_posts = Post.objects.filter(status='published', category__name='Builds').order_by('-created_at')[:3]
    news_posts = Post.objects.filter(status='published', category__name='News').order_by('-created_at')[:3]
    
=======
from django.shortcuts import render
from apps.posts.models import Post, Category

def post_list(request):
    new_posts = Post.objects.filter(status='published').order_by('-created_at')[:4]

    harley_posts = Post.objects.filter(status='published', category__name='Harley Davidson').order_by('-created_at')[:6]

    build_posts = Post.objects.filter(status='published', category__name='Builds').order_by('-created_at')[:3]

    news_posts = Post.objects.filter(status='published', category__name='News').order_by('-created_at')[:3]

>>>>>>> origin/main
    context = {
        'new_posts': new_posts,
        'harley_posts': harley_posts,
        'build_posts': build_posts,
        'news_posts': news_posts,
    }
<<<<<<< HEAD
    return render(request, 'posts/post_list.html', context)
=======

    return render(request, 'posts/post_list.html', context)   
>>>>>>> origin/main
