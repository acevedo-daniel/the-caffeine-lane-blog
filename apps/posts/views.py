from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Count
from django.http import Http404, JsonResponse, HttpResponseForbidden
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User

from .models import Post, Comment, Category
from .forms import PostForm, CommentForm, PostSearchForm, CommentReplyForm
from .mixins import AuthorRequiredMixin, StaffRequiredMixin


# ==============================================
# VISTAS DE LISTADO DE POSTS
# ==============================================

class PostListView(ListView):
    """Vista principal para listar posts"""
    model = Post
    template_name = 'posts/post_list.html'
    context_object_name = 'posts'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Post.objects.published().select_related('author').prefetch_related('category', 'comments')
        
        # Filtros de búsqueda
        search_query = self.request.GET.get('search')
        category_slug = self.request.GET.get('category')
        sort_by = self.request.GET.get('sort', 'newest')
        
        if search_query:
            queryset = queryset.search(search_query)
        
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        # Ordenamiento
        sort_options = {
            'newest': '-created_at',
            'oldest': 'created_at',
            'most_commented': '-comments_count',
            'most_viewed': '-views_count',
            'title_asc': 'title',
            'title_desc': '-title',
        }
        
        if sort_by in sort_options:
            if sort_by == 'most_commented':
                queryset = queryset.annotate(
                    comments_count=Count('comments', filter=Q(comments__is_active=True))
                ).order_by(sort_options[sort_by])
            else:
                queryset = queryset.order_by(sort_options[sort_by])
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = PostSearchForm(self.request.GET or None)
        context['categories'] = Category.objects.filter(is_active=True)
        context['current_category'] = self.request.GET.get('category')
        context['current_search'] = self.request.GET.get('search')
        context['current_sort'] = self.request.GET.get('sort', 'newest')
        
        # Estadísticas
        context['total_posts'] = Post.objects.published().count()
        
        return context


class PostByCategoryView(PostListView):
    """Vista para posts por categoría"""
    template_name = 'posts/post_by_category.html'
    
    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs['category_slug'], is_active=True)
        return super().get_queryset().filter(category=self.category)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        context['page_title'] = f"Posts en {self.category.name}"
        return context


# ==============================================
# VISTA DE DETALLE DE POST
# ==============================================

class PostDetailView(DetailView):
    """Vista de detalle de post con comentarios"""
    model = Post
    template_name = 'posts/post_detail.html'
    context_object_name = 'post'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_queryset(self):
        queryset = Post.objects.select_related('author').prefetch_related(
            'category', 
            'comments__author',
            'comments__replies__author'
        )
        
        # Solo mostrar posts publicados (excepto al autor o staff)
        if self.request.user.is_authenticated:
            if self.request.user.is_staff:
                return queryset  # Staff puede ver todos
            # El autor puede ver sus propios posts
            return queryset.filter(
                Q(status='published') | Q(author=self.request.user)
            )
        
        return queryset.filter(status='published')
    
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        
        # Incrementar contador de visualizaciones
        if not self.request.user.is_authenticated or self.request.user != obj.author:
            obj.increment_views()
        
        return obj
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.object
        
        # Comentarios activos de nivel superior
        comments = post.comments.filter(is_active=True, parent=None).select_related('author').prefetch_related('replies__author')
        context['comments'] = comments
        
        # Formulario de comentarios
        if self.request.user.is_authenticated and post.allow_comments:
            context['comment_form'] = CommentForm()
        
        # Posts relacionados
        related_posts = Post.objects.published().filter(
            category__in=post.category.all()
        ).exclude(pk=post.pk).distinct()[:3]
        context['related_posts'] = related_posts
        
        # Información adicional
        context['can_edit'] = post.can_edit(self.request.user)
        context['can_delete'] = post.can_delete(self.request.user)
        context['reading_time'] = post.get_reading_time()
        
        return context


# ==============================================
# VISTAS DE CREACIÓN Y EDICIÓN DE POSTS
# ==============================================

class PostCreateView(LoginRequiredMixin, CreateView):
    """Vista para crear posts"""
    model = Post
    form_class = PostForm
    template_name = 'posts/post_create.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, 'Post creado exitosamente.')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Por favor, corrige los errores en el formulario.')
        return super().form_invalid(form)
    
    def get_success_url(self):
        if self.object.status == 'published':
            return self.object.get_absolute_url()
        else:
            return reverse('post_list')


class PostUpdateView(LoginRequiredMixin, AuthorRequiredMixin, UpdateView):
    """Vista para editar posts"""
    model = Post
    form_class = PostForm
    template_name = 'posts/post_update.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        messages.success(self.request, 'Post actualizado exitosamente.')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Por favor, corrige los errores en el formulario.')
        return super().form_invalid(form)
    
    def get_success_url(self):
        return self.object.get_absolute_url()


class PostDeleteView(LoginRequiredMixin, AuthorRequiredMixin, DeleteView):
    """Vista para eliminar posts"""
    model = Post
    template_name = 'posts/post_delete.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    success_url = reverse_lazy('post_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Post eliminado exitosamente.')
        return super().delete(request, *args, **kwargs)


# ==============================================
# VISTAS DE COMENTARIOS
# ==============================================

@login_required
@csrf_protect
def add_comment(request, slug):
    """Vista para agregar comentarios"""
    post = get_object_or_404(Post, slug=slug, status='published')
    
    if not post.allow_comments:
        messages.error(request, 'Los comentarios están deshabilitados para este post.')
        return redirect('post_detail', slug=slug)
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            
            messages.success(request, 'Comentario agregado exitosamente.')
            return redirect('post_detail', slug=slug)
        else:
            messages.error(request, 'Error al agregar el comentario. Por favor, revisa el formulario.')
    
    return redirect('post_detail', slug=slug)


@login_required
@csrf_protect
def reply_comment(request, slug, comment_id):
    """Vista para responder comentarios"""
    post = get_object_or_404(Post, slug=slug, status='published')
    parent_comment = get_object_or_404(Comment, pk=comment_id, post=post, is_active=True)
    
    if not post.allow_comments:
        messages.error(request, 'Los comentarios están deshabilitados para este post.')
        return redirect('post_detail', slug=slug)
    
    if request.method == 'POST':
        form = CommentReplyForm(request.POST, post=post)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.parent = parent_comment
            comment.save()
            
            messages.success(request, 'Respuesta agregada exitosamente.')
            return redirect('post_detail', slug=slug)
        else:
            messages.error(request, 'Error al agregar la respuesta.')
    
    return redirect('post_detail', slug=slug)


class CommentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Vista para editar comentarios"""
    model = Comment
    form_class = CommentForm
    template_name = 'posts/comment_update.html'
    
    def test_func(self):
        comment = self.get_object()
        return comment.can_edit(self.request.user)
    
    def form_valid(self, form):
        comment = form.save(commit=False)
        comment.is_edited = True
        comment.save()
        messages.success(self.request, 'Comentario actualizado exitosamente.')
        return redirect('post_detail', slug=comment.post.slug)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Error al actualizar el comentario.')
        return super().form_invalid(form)


class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Vista para eliminar comentarios"""
    model = Comment
    template_name = 'posts/comment_delete.html'
    
    def test_func(self):
        comment = self.get_object()
        return comment.can_delete(self.request.user)
    
    def get_success_url(self):
        return reverse('post_detail', kwargs={'slug': self.object.post.slug})
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Comentario eliminado exitosamente.')
        return super().delete(request, *args, **kwargs)


# ==============================================
# VISTAS AJAX Y UTILIDADES
# ==============================================

@require_POST
@login_required
def toggle_comment_status(request, comment_id):
    """Vista AJAX para activar/desactivar comentarios (solo staff)"""
    if not request.user.is_staff:
        return JsonResponse({'error': 'No tienes permisos'}, status=403)
    
    comment = get_object_or_404(Comment, pk=comment_id)
    comment.is_active = not comment.is_active
    comment.save()
    
    return JsonResponse({
        'success': True,
        'is_active': comment.is_active,
        'message': 'Comentario activado' if comment.is_active else 'Comentario desactivado'
    })


def post_search_ajax(request):
    """Vista AJAX para búsqueda de posts"""
    query = request.GET.get('q', '').strip()
    
    if not query or len(query) < 2:
        return JsonResponse({'results': []})
    
    posts = Post.objects.published().search(query)[:10]
    
    results = []
    for post in posts:
        results.append({
            'id': post.id,
            'title': post.title,
            'url': post.get_absolute_url(),
            'excerpt': post.excerpt or post.generate_excerpt()[:100],
            'author': post.author.username,
            'created_at': post.created_at.strftime('%d/%m/%Y')
        })
    
    return JsonResponse({'results': results})


# ==============================================
# VISTAS DE USUARIO Y DASHBOARD
# ==============================================

class UserPostsView(LoginRequiredMixin, ListView):
    """Vista para posts del usuario actual"""
    model = Post
    template_name = 'posts/user_posts.html'
    context_object_name = 'posts'
    paginate_by = 10
    
    def get_queryset(self):
        return Post.objects.filter(author=self.request.user).order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_posts = self.get_queryset()
        
        context['stats'] = {
            'total_posts': user_posts.count(),
            'published_posts': user_posts.filter(status='published').count(),
            'draft_posts': user_posts.filter(status='draft').count(),
            'total_views': sum(post.views_count for post in user_posts),
            'total_comments': sum(post.get_comments_count() for post in user_posts),
        }
        
        return context


class AuthorPostsView(ListView):
    """Vista pública de posts por autor"""
    model = Post
    template_name = 'posts/author_posts.html'
    context_object_name = 'posts'
    paginate_by = 10
    
    def get_queryset(self):
        self.author = get_object_or_404(User, username=self.kwargs['username'])
        return Post.objects.published().filter(author=self.author).order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['author'] = self.author
        context['posts_count'] = self.get_queryset().count()
        return context


# ==============================================
# VISTAS DE FEEDS Y SITEMAP (para SEO)
# ==============================================

def latest_posts_feed(request):
    """Feed RSS de los últimos posts"""
    from django.contrib.syndication.views import Feed
    from django.urls import reverse
    
    class LatestPostsFeed(Feed):
        title = "The Caffeine Lane - Últimos Posts"
        link = "/posts/"
        description = "Los últimos posts del blog de motos The Caffeine Lane"
        
        def items(self):
            return Post.objects.published()[:10]
        
        def item_title(self, item):
            return item.title
        
        def item_description(self, item):
            return item.excerpt or item.generate_excerpt()
        
        def item_link(self, item):
            return item.get_absolute_url()
    
    feed = LatestPostsFeed()
    return feed(request)


# ==============================================
# VISTAS DE ERROR PERSONALIZADAS
# ==============================================

def post_not_found(request, exception=None):
    """Vista personalizada para posts no encontrados"""
    return render(request, 'posts/post_not_found.html', status=404)