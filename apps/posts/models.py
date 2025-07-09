from django.db import models

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