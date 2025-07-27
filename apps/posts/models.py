from django.db import models
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