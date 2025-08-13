from django.contrib import admin
from django.db.models import Count, Q
from django.urls import reverse
from django.utils.html import format_html
from django.utils import timezone  # Importación de timezone
from django.utils.safestring import mark_safe

from .models import Category, Post, Comment


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'color_preview', 'posts_count', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at',)
    ordering = ('name',)

    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'description')
        }),
        ('Configuración', {
            'fields': ('color', 'is_active')
        }),
        ('Metadatos', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(posts_count_annotated=Count('post'))

    def color_preview(self, obj):
        return format_html(
            '<div style="width: 20px; height: 20px; background-color: {}; border-radius: 3px; border: 1px solid #ccc;"></div>',
            obj.color
        )
    color_preview.short_description = 'Color'

    def posts_count(self, obj):
        count = obj.posts_count_annotated
        if count > 0:
            url = reverse('admin:posts_post_changelist') + f'?category__id__exact={obj.id}'
            return format_html('<a href="{}">{} posts</a>', url, count)
        return '0 posts'
    posts_count.short_description = 'Posts'
    posts_count.admin_order_field = 'posts_count_annotated'


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'author', 'status', 'is_featured',
        'views_count', 'comments_count', 'created_at'
    )
    list_filter = (
        'status', 'is_featured', 'allow_comments',
        'category', 'created_at', 'author'
    )
    search_fields = ('title', 'content', 'author__username', 'author__email')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = (
        'views_count', 'created_at', 'updated_at',
        'published_at', 'get_reading_time'
    )
    filter_horizontal = ('category',)
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)

    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'author', 'content')
        }),
        ('Contenido adicional', {
            'fields': ('excerpt', 'image'),
            'classes': ('collapse',)
        }),
        ('Categorización', {
            'fields': ('category',)
        }),
        ('Configuración', {
            'fields': ('status', 'is_featured', 'allow_comments')
        }),
        ('SEO', {
            'fields': ('meta_description', 'meta_keywords'),
            'classes': ('collapse',)
        }),
        ('Estadísticas', {
            'fields': ('views_count', 'get_reading_time'),
            'classes': ('collapse',)
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at', 'published_at'),
            'classes': ('collapse',)
        })
    )

    actions = ['make_published', 'make_draft', 'make_featured', 'remove_featured']

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('author').prefetch_related('category').annotate(
            comments_count=Count('comments', filter=Q(comments__is_active=True))
        )

    def comments_count(self, obj):
        count = obj.comments_count
        if count > 0:
            url = reverse('admin:posts_comment_changelist') + f'?post__id__exact={obj.id}'
            return format_html('<a href="{}">{}</a>', url, count)
        return '0'
    comments_count.short_description = 'Comentarios'
    comments_count.admin_order_field = 'comments_count'

    def get_reading_time(self, obj):
        return f"{obj.get_reading_time()} min"
    get_reading_time.short_description = 'Tiempo lectura'

    def make_published(self, request, queryset):
        updated = queryset.update(status='published', published_at=timezone.now())
        self.message_user(request, f'{updated} posts marcados como publicados.')
    make_published.short_description = 'Publicar posts seleccionados'

    def make_draft(self, request, queryset):
        updated = queryset.update(status='draft')
        self.message_user(request, f'{updated} posts cambiados a borrador.')
    make_draft.short_description = 'Cambiar a borrador'

    def make_featured(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} posts marcados como destacados.')
    make_featured.short_description = 'Marcar como destacados'

    def remove_featured(self, request, queryset):
        updated = queryset.update(is_featured=False)
        self.message_user(request, f'{updated} posts desmarcados como destacados.')
    remove_featured.short_description = 'Quitar destacado'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'content_preview', 'author', 'post_title', 'is_active',
        'is_reply', 'created_at'
    )
    list_filter = ('is_active', 'is_edited', 'created_at', 'post__category')
    search_fields = (
        'content', 'author__username', 'author__email',
        'post__title'
    )
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)

    fieldsets = (
        (None, {
            'fields': ('author', 'post', 'content')
        }),
        ('Configuración', {
            'fields': ('is_active', 'is_edited', 'parent')
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    actions = ['activate_comments', 'deactivate_comments']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('author', 'post', 'parent')

    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Contenido'

    def post_title(self, obj):
        url = reverse('admin:posts_post_change', args=[obj.post.pk])
        return format_html('<a href="{}">{}</a>', url, obj.post.title)
    post_title.short_description = 'Post'
    post_title.admin_order_field = 'post__title'

    def is_reply(self, obj):
        return obj.parent is not None
    is_reply.short_description = 'Es respuesta'
    is_reply.boolean = True
    is_reply.admin_order_field = 'parent'

    def activate_comments(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} comentarios activados.')
    activate_comments.short_description = 'Activar comentarios'

    def deactivate_comments(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} comentarios desactivados.')
    deactivate_comments.short_description = 'Desactivar comentarios'


# Personalización global del admin
admin.site.site_header = "The Caffeine Lane - Administración"
admin.site.site_title = "TCL Admin"
admin.site.index_title = "Panel de Control"