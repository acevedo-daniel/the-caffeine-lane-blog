
from django.apps import AppConfig

class PostsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.posts'

    def ready(self):
        from .models import Category, Post, Comment
        # Si querés conectar señales, lo hacés acá


    # ...existing code...
