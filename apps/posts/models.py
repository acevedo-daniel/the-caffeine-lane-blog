from django.db import models
<<<<<<< HEAD
from django.contrib.auth.models import User
from django.urls import reverse

# Create your models here.

# Definir la clase Post

# Definir la clase Comentario
class Comentario(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comentarios')
    autor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comentarios')
    contenido = models.TextField(max_length=500)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)
    comentario_padre = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='respuestas')
    
    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name = 'Comentario'
        verbose_name_plural = 'Comentarios'
    
    def __str__(self):
        return f'Comentario de {self.autor.username} en {self.post.titulo}'
    
    def es_respuesta(self):
        return self.comentario_padre is not None
=======

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, null=False, blank=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ['name']

class Post(models.Model):
    title = models.CharField(max_length=200, null=False, blank=False)
    subtitle = models.CharField(max_length=300, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    text = models.TextField(null=False, blank=False)
    status = models.BooleanField(default=True)
    categoriy = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=None
    )
    imagen = models.ImageField(
        upload_to='posts_images/',
        null=True,
        blank=True,
        default='static/default_post_image.png'
    )
    publication_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Post"
        verbose_name_plural = "Posts"
        ordering = ['-publication_date']

    # Método para eliminar la imagen asociada cuando se elimina el post
    def delete(self, *args, **kwargs):
        # Si el post tiene una imagen y no es la imagen por defecto, elimínala del sistema de archivos
        if self.imagen and self.imagen.name != 'static/default_post_image.png':
            if os.path.exists(self.imagen.path):
                os.remove(self.imagen.path)
        super().delete(*args, **kwargs) # Llama al método delete original de Django
>>>>>>> ec61b933ec35f8b9360d6f874869a62671d0a1bc
