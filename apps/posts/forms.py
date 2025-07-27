from django import forms
from .models import Comentario

# Definir el formulario para los Posts

# Definir el formulario para los Comentarios
class ComentarioForm(forms.ModelForm):
    class Meta:
        models = Comentario
        fields = ['contenido']
        widgets = {
            'contenido': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': '¿Qué opinas sobre esta moto?'
            })
        }