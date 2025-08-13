from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db import models # Añadido: Importación de models para Q object


class AuthorRequiredMixin(UserPassesTestMixin):
    """Mixin que permite acceso solo al autor del post o al staff"""
    
    def test_func(self):
        obj = self.get_object()
        user = self.request.user
        return user.is_authenticated and (user == obj.author or user.is_staff)
    
    def handle_no_permission(self):
        messages.error(self.request, 'No tienes permisos para realizar esta acción.')
        return redirect('post_list')


class StaffRequiredMixin(UserPassesTestMixin):
    """Mixin que permite acceso solo al staff"""
    
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_staff
    
    def handle_no_permission(self):
        messages.error(self.request, 'Necesitas permisos de administrador para acceder a esta página.')
        return redirect('post_list')


class CommentAuthorMixin(UserPassesTestMixin):
    """Mixin que permite acceso solo al autor del comentario o al staff"""
    
    def test_func(self):
        comment = self.get_object()
        user = self.request.user
        return user.is_authenticated and (user == comment.author or user.is_staff)
    
    def handle_no_permission(self):
        messages.error(self.request, 'No tienes permisos para editar este comentario.')
        return redirect('post_detail', slug=self.get_object().post.slug)


class PublishedPostMixin:
    """Mixin para filtrar solo posts publicados"""
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Si es staff o el autor, puede ver todos sus posts
        if self.request.user.is_authenticated:
            if self.request.user.is_staff:
                return queryset
            # Filtrar posts publicados o del usuario actual
            return queryset.filter(
                models.Q(status='published') | models.Q(author=self.request.user)
            )
        
        # Usuario anónimo solo ve posts publicados
        return queryset.filter(status='published')
