import os
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils import timezone
from PIL import Image
from django.core.exceptions import ValidationError


def post_image_path(instance, filename):
    """Generar path dinámico para imágenes de posts"""
    extension = os.path.splitext(filename)[1]
    # Usar el slug del post si existe, sino generar uno temporal
    slug = instance.slug or slugify(instance.title)
    new_filename = f"{slug}{extension}"
    return f"posts/media/{new_filename}"


def validate_image_size(image):
    """Validar tamaño máximo de imagen (5MB)"""
    max_size = 5 * 1024 * 1024  # 5MB
    if image.size > max_size:
        raise ValidationError("La imagen no puede ser mayor a 5MB.")


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Nombre")
    slug = models.SlugField(max_length=120, unique=True, blank=True, verbose_name="Slug")
    description = models.TextField(blank=True, verbose_name="Descripción")
    color = models.CharField(max_length=7, default="#000000", verbose_name="Color", 
                           help_text="Color hexadecimal para la categoría")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creado")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('post_by_category', kwargs={'category_slug': self.slug})

    def get_posts_count(self):
        """Obtener número de posts publicados en esta categoría"""
        return self.post_set.filter(status='published').count()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ["name"]


class PostQuerySet(models.QuerySet):
    """Custom QuerySet para Posts"""
    
    def published(self):
        return self.filter(status='published')
    
    def draft(self):
        return self.filter(status='draft')
    
    def by_author(self, user):
        return self.filter(author=user)
    
    def by_category(self, category):
        return self.filter(category=category)
    
    def recent(self, days=30):
        return self.filter(created_at__gte=timezone.now() - timezone.timedelta(days=days))
    
    def search(self, query):
        return self.filter(
            models.Q(title__icontains=query) |
            models.Q(content__icontains=query)
        )


class PostManager(models.Manager):
    """Custom Manager para Posts"""
    
    def get_queryset(self):
        return PostQuerySet(self.model, using=self._db)
    
    def published(self):
        return self.get_queryset().published()
    
    def draft(self):
        return self.get_queryset().draft()
    
    def by_author(self, user):
        return self.get_queryset().by_author(user)
    
    def by_category(self, category):
        return self.get_queryset().by_category(category)
    
    def recent(self, days=30):
        return self.get_queryset().recent(days)
    
    def search(self, query):
        return self.get_queryset().search(query)
    
    def featured(self):
        """Posts destacados para el carrusel"""
        return self.published().filter(is_featured=True).order_by('-created_at')


class Post(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Borrador'),
        ('published', 'Publicado'),
        ('archived', 'Archivado'),
    ]
    
    # Campos básicos
    title = models.CharField(max_length=200, verbose_name="Título")
    slug = models.SlugField(max_length=250, unique=True, blank=True, verbose_name="Slug")
    content = models.TextField(verbose_name="Contenido")
    excerpt = models.CharField(max_length=300, blank=True, verbose_name="Extracto", help_text="Breve descripción del post para mostrar en listados")

    # Relaciones
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Autor")
    category = models.ManyToManyField(Category, verbose_name="Categorías")
    
    # Media
    image = models.ImageField(
        upload_to=post_image_path, 
        null=True, 
        blank=True, 
        verbose_name="Imagen destacada",
        validators=[validate_image_size],
        help_text="Imagen principal del post (máx. 5MB)"
    )
    
    # Estados y configuración
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft', verbose_name="Estado")
    is_featured = models.BooleanField(default=False, verbose_name="Destacado",
                                     help_text="Mostrar en carrusel principal")
    allow_comments = models.BooleanField(default=True, verbose_name="Permitir comentarios")
    
    # SEO y metadata
    meta_description = models.CharField(max_length=160, blank=True, verbose_name="Meta descripción",
                                       help_text="Descripción para motores de búsqueda")
    meta_keywords = models.CharField(max_length=200, blank=True, verbose_name="Palabras clave",
                                    help_text="Separadas por comas")
    
    # Fechas
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creado")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Actualizado")
    published_at = models.DateTimeField(null=True, blank=True, verbose_name="Publicado")
    
    # Estadísticas (se pueden actualizar via signals o tasks)
    views_count = models.PositiveIntegerField(default=0, verbose_name="Visualizaciones")
    
    # Managers
    objects = PostManager()
    
    def save(self, *args, **kwargs):
        # Generar slug automáticamente
        if not self.slug:
            self.slug = self.generate_unique_slug()
        
        # Establecer fecha de publicación
        if self.status == 'published' and not self.published_at:
            self.published_at = timezone.now()
        elif self.status != 'published':
            self.published_at = None
            
        # Generar excerpt si no existe
        if not self.excerpt:
            self.excerpt = self.generate_excerpt()
        
        super().save(*args, **kwargs)
        
        # Redimensionar imagen si es necesario
        if self.image:
            self.resize_image()
    
    def generate_unique_slug(self):
        """Generar slug único"""
        base_slug = slugify(self.title)
        slug = base_slug
        counter = 1
        
        while Post.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
            
        return slug
    
    def generate_excerpt(self):
        """Generar excerpt automático desde el contenido"""
        import re
        # Remover HTML tags si los hay
        clean_content = re.sub(r'<[^>]+>', '', self.content)
        # Tomar las primeras 200 caracteres
        excerpt = clean_content[:200]
        if len(clean_content) > 200:
            excerpt += "..."
        return excerpt
    
    def resize_image(self):
        """Redimensionar imagen para optimizar tamaño"""
        if not self.image:
            return
            
        try:
            img = Image.open(self.image.path)
            
            # Tamaño máximo
            max_size = (1200, 800)
            
            if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
                img.save(self.image.path, optimize=True, quality=85)
        except Exception as e:
            print(f"Error redimensionando imagen: {e}")
    
    def get_absolute_url(self):
        return reverse('post_detail', kwargs={'slug': self.slug})
    
    def get_edit_url(self):
        return reverse('post_update', kwargs={'slug': self.slug})
    
    def get_delete_url(self):
        return reverse('post_delete', kwargs={'slug': self.slug})
    
    def get_reading_time(self):
        """Calcular tiempo estimado de lectura"""
        word_count = len(self.content.split())
        reading_time = max(1, round(word_count / 200))  # 200 palabras por minuto
        return reading_time
    
    def get_active_comments(self):
        """Obtener comentarios activos (no respuestas)"""
        return self.comments.filter(is_active=True, parent=None)
    
    def get_comments_count(self):
        """Obtener número total de comentarios"""
        return self.comments.filter(is_active=True).count()
    
    def can_edit(self, user):
        """Verificar si el usuario puede editar el post"""
        return user.is_authenticated and (user == self.author or user.is_staff)
    
    def can_delete(self, user):
        """Verificar si el usuario puede eliminar el post"""
        return user.is_authenticated and (user == self.author or user.is_staff)
    
    def increment_views(self):
        """Incrementar contador de visualizaciones"""
        self.views_count += 1
        self.save(update_fields=['views_count'])
    
    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Post"
        verbose_name_plural = "Posts"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['slug']),
        ]


class CommentQuerySet(models.QuerySet):
    """Custom QuerySet para Comments"""
    
    def active(self):
        return self.filter(is_active=True)
    
    def by_author(self, user):
        return self.filter(author=user)
    
    def by_post(self, post):
        return self.filter(post=post)
    
    def top_level(self):
        """Comentarios de nivel superior (no respuestas)"""
        return self.filter(parent=None)
    
    def replies(self):
        """Solo respuestas"""
        return self.exclude(parent=None)


class CommentManager(models.Manager):
    """Custom Manager para Comments"""
    
    def get_queryset(self):
        return CommentQuerySet(self.model, using=self._db)
    
    def active(self):
        return self.get_queryset().active()
    
    def by_author(self, user):
        return self.get_queryset().by_author(user)
    
    def by_post(self, post):
        return self.get_queryset().by_post(post)
    
    def top_level(self):
        return self.get_queryset().top_level()


class Comment(models.Model):
    # Relaciones
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments", verbose_name="Post")
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Autor")
    parent = models.ForeignKey(
        "self", 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name="replies",
        verbose_name="Comentario padre"
    )
    
    # Contenido
    content = models.TextField(max_length=1000, verbose_name="Contenido")
    
    # Estados
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    is_edited = models.BooleanField(default=False, verbose_name="Editado")
    
    # Fechas
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creado")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Actualizado")
    
    # Manager
    objects = CommentManager()
    
    def save(self, *args, **kwargs):
        # Marcar como editado si se está actualizando el contenido
        if self.pk and 'content' in kwargs.get('update_fields', []):
            self.is_edited = True
        
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return f"{self.post.get_absolute_url()}#comment-{self.id}"
    
    def get_edit_url(self):
        return reverse('comment_update', kwargs={'pk': self.pk})
    
    def get_delete_url(self):
        return reverse('comment_delete', kwargs={'pk': self.pk})
    
    def can_edit(self, user):
        """Verificar si el usuario puede editar el comentario"""
        return user.is_authenticated and (user == self.author or user.is_staff)
    
    def can_delete(self, user):
        """Verificar si el usuario puede eliminar el comentario"""
        return user.is_authenticated and (user == self.author or user.is_staff)
    
    def get_reply_count(self):
        """Obtener número de respuestas"""
        return self.replies.filter(is_active=True).count()
    
    def is_reply(self):
        """Verificar si es una respuesta a otro comentario"""
        return self.parent is not None
    
    def get_level(self):
        """Obtener nivel de anidación del comentario"""
        if not self.parent:
            return 0
        return self.parent.get_level() + 1
    
    def __str__(self):
        return f"Comentario de {self.author.username} en {self.post.title}"

    class Meta:
        verbose_name = "Comentario"
        verbose_name_plural = "Comentarios"
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=['post', 'is_active']),
            models.Index(fields=['author']),
            models.Index(fields=['created_at']),
        ]