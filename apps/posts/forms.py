from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from .models import Post, Comment, Category
import re


class PostForm(forms.ModelForm):
    """Formulario para crear y editar posts"""
    
    # Campos adicionales para mejor UX
    tags = forms.CharField(
        max_length=200,
        required=False,
        help_text="Separar tags con comas",
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'motorucci, kawasaki, build, custom',
            'data-toggle': 'tooltip',
            'title': 'Palabras clave separadas por comas'
        })
    )
    
    class Meta:
        model = Post
        fields = [
            'title', 'content', 'excerpt', 'image', 'category', 
            'status', 'is_featured', 'allow_comments', 
            'meta_description', 'meta_keywords'
        ]
        
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Título del post...',
                'maxlength': 200,
                'required': True
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-input form-textarea',
                'placeholder': 'Escribe el contenido de tu post aquí...',
                'rows': 15,
                'required': True
            }),
            'excerpt': forms.Textarea(attrs={
                'class': 'form-input',
                'placeholder': 'Breve descripción del post (opcional)...',
                'rows': 3,
                'maxlength': 300
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-input form-file',
                'accept': 'image/*'
            }),
            'category': forms.CheckboxSelectMultiple(attrs={
                'class': 'form-checkbox-list'
            }),
            'status': forms.Select(attrs={
                'class': 'form-input form-select'
            }),
            'is_featured': forms.CheckboxInput(attrs={
                'class': 'form-checkbox'
            }),
            'allow_comments': forms.CheckboxInput(attrs={
                'class': 'form-checkbox'
            }),
            'meta_description': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Descripción para motores de búsqueda...',
                'maxlength': 160
            }),
            'meta_keywords': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'palabras, clave, separadas, por, comas',
                'maxlength': 200
            }),
        }
        
        labels = {
            'title': 'Título del Post',
            'content': 'Contenido',
            'excerpt': 'Extracto',
            'image': 'Imagen Destacada',
            'category': 'Categorías',
            'status': 'Estado',
            'is_featured': 'Post Destacado',
            'allow_comments': 'Permitir Comentarios',
            'meta_description': 'Meta Descripción',
            'meta_keywords': 'Palabras Clave',
        }
        
        help_texts = {
            'title': 'Título llamativo y descriptivo para tu post',
            'content': 'Contenido principal del post. Puedes usar markdown básico.',
            'excerpt': 'Resumen corto que aparecerá en las listas de posts',
            'image': 'Imagen principal del post (máximo 5MB)',
            'category': 'Selecciona una o más categorías',
            'is_featured': 'Marcar para mostrar en el carrusel principal',
            'allow_comments': 'Permitir que los usuarios comenten este post',
            'meta_description': 'Descripción para SEO (160 caracteres máximo)',
            'meta_keywords': 'Palabras clave para SEO, separadas por comas',
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filtrar categorías activas
        self.fields['category'].queryset = Category.objects.filter(is_active=True)
        
        # Solo staff puede marcar como destacado
        if self.user and not self.user.is_staff:
            self.fields['is_featured'].widget = forms.HiddenInput()
            self.fields['is_featured'].initial = False
        
        # Cargar tags existentes si estamos editando
        if self.instance.pk:
            self.fields['tags'].initial = self.instance.meta_keywords

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if not title:
            raise ValidationError("El título es obligatorio.")
        
        if len(title) < 5:
            raise ValidationError("El título debe tener al menos 5 caracteres.")
        
        # Verificar títulos duplicados (excepto el actual)
        existing = Post.objects.filter(title__iexact=title)
        if self.instance.pk:
            existing = existing.exclude(pk=self.instance.pk)
        
        if existing.exists():
            raise ValidationError("Ya existe un post con este título.")
        
        return title.strip()

    def clean_content(self):
        content = self.cleaned_data.get('content')
        if not content:
            raise ValidationError("El contenido es obligatorio.")
        
        if len(content.strip()) < 50:
            raise ValidationError("El contenido debe tener al menos 50 caracteres.")
        
        # Validación básica de contenido malicioso
        dangerous_patterns = [
            r'<script.*?>.*?</script>',
            r'javascript:',
            r'on\w+\s*=',
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                raise ValidationError("El contenido contiene elementos no permitidos.")
        
        return content.strip()

    def clean_excerpt(self):
        excerpt = self.cleaned_data.get('excerpt')
        if excerpt and len(excerpt) > 300:
            raise ValidationError("El extracto no puede exceder 300 caracteres.")
        return excerpt.strip() if excerpt else ''

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            # Validar tamaño
            if image.size > 5 * 1024 * 1024:  # 5MB
                raise ValidationError("La imagen no puede ser mayor a 5MB.")
            
            # Validar tipo
            allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
            if hasattr(image, 'content_type') and image.content_type not in allowed_types:
                raise ValidationError("Solo se permiten imágenes JPG, PNG, GIF o WebP.")
        
        return image

    def clean_meta_description(self):
        meta_desc = self.cleaned_data.get('meta_description')
        if meta_desc and len(meta_desc) > 160:
            raise ValidationError("La meta descripción no puede exceder 160 caracteres.")
        return meta_desc.strip() if meta_desc else ''

    def clean_category(self):
        categories = self.cleaned_data.get('category')
        if not categories or len(categories) == 0:
            raise ValidationError("Debes seleccionar al menos una categoría.")
        if len(categories) > 3:
            raise ValidationError("No puedes seleccionar más de 3 categorías.")
        return categories

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        
        # Si se está publicando, validar campos obligatorios
        if status == 'published':
            required_fields = ['title', 'content']
            for field in required_fields:
                if not cleaned_data.get(field):
                    self.add_error(field, f"El campo es obligatorio para publicar.") # Mejorado para adjuntar el error al campo específico
        
        return cleaned_data

    def save(self, commit=True):
        post = super().save(commit=False)
        
        # Procesar tags
        tags = self.cleaned_data.get('tags', '')
        if tags:
            # Limpiar y procesar tags
            tag_list = [tag.strip().lower() for tag in tags.split(',') if tag.strip()]
            post.meta_keywords = ', '.join(tag_list[:10])  # Máximo 10 tags
        
        if commit:
            post.save()
            self.save_m2m()  # Guardar relaciones ManyToMany
        
        return post


class CommentForm(forms.ModelForm):
    """Formulario para crear y editar comentarios"""
    
    class Meta:
        model = Comment
        fields = ['content']
        
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-input form-textarea',
                'placeholder': 'Escribe tu comentario aquí...',
                'rows': 4,
                'maxlength': 1000,
                'required': True
            })
        }
        
        labels = {
            'content': 'Tu Comentario'
        }

    def clean_content(self):
        content = self.cleaned_data.get('content')
        if not content:
            raise ValidationError("El comentario no puede estar vacío.")
        
        content = content.strip()
        
        if len(content) < 3:
            raise ValidationError("El comentario debe tener al menos 3 caracteres.")
        
        if len(content) > 1000:
            raise ValidationError("El comentario no puede exceder 1000 caracteres.")
        
        # Validación anti-spam básica
        spam_patterns = [
            r'https?://[^\s]+',  # URLs
            r'\b(?:buy|sell|click|visit|free|win|prize)\b',  # Palabras spam comunes
        ]
        
        spam_count = 0
        for pattern in spam_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                spam_count += 1
        
        if spam_count > 2:
            raise ValidationError("El comentario parece contener spam.")
        
        return content


class PostSearchForm(forms.Form):
    """Formulario para búsqueda y filtrado de posts"""
    
    search = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input search-input',
            'placeholder': 'Buscar posts...',
            'id': 'search-input'
        })
    )
    
    category = forms.ModelChoiceField(
        queryset=Category.objects.filter(is_active=True),
        required=False,
        empty_label="Todas las categorías",
        widget=forms.Select(attrs={
            'class': 'form-input form-select filter-select',
            'id': 'category-filter'
        })
    )
    
    sort = forms.ChoiceField(
        choices=[
            ('newest', 'Más recientes'),
            ('oldest', 'Más antiguos'),
            ('most_commented', 'Más comentados'),
            ('most_viewed', 'Más vistos'),
            ('title_asc', 'Título A-Z'),
            ('title_desc', 'Título Z-A'),
        ],
        required=False,
        initial='newest',
        widget=forms.Select(attrs={
            'class': 'form-input form-select filter-select',
            'id': 'sort-filter'
        })
    )

    def clean_search(self):
        search = self.cleaned_data.get('search')
        if search:
            search = search.strip()
            if len(search) < 2:
                raise ValidationError("La búsqueda debe tener al menos 2 caracteres.")
        return search


class CommentReplyForm(CommentForm):
    """Formulario específico para responder comentarios"""
    
    parent = forms.ModelChoiceField(
        queryset=Comment.objects.all(),
        widget=forms.HiddenInput()
    )
    
    class Meta(CommentForm.Meta):
        fields = ['content', 'parent']

    def __init__(self, *args, **kwargs):
        self.post = kwargs.pop('post', None)
        super().__init__(*args, **kwargs)
        
        if self.post:
            # Filtrar solo comentarios de este post
            self.fields['parent'].queryset = Comment.objects.filter(post=self.post)

    def clean_parent(self):
        parent = self.cleaned_data.get('parent')
        if parent and parent.post != self.post:
            raise ValidationError("Comentario padre inválido.")
        return parent


class CategoryForm(forms.ModelForm):
    """Formulario para crear y editar categorías (solo admin)"""
    
    class Meta:
        model = Category
        fields = ['name', 'description', 'color', 'is_active']
        
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Nombre de la categoría...'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-input',
                'placeholder': 'Descripción de la categoría...',
                'rows': 3
            }),
            'color': forms.TextInput(attrs={
                'class': 'form-input',
                'type': 'color',
                'value': '#000000'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-checkbox'
            })
        }

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name:
            raise ValidationError("El nombre es obligatorio.")
        
        # Verificar nombres duplicados
        existing = Category.objects.filter(name__iexact=name)
        if self.instance.pk:
            existing = existing.exclude(pk=self.instance.pk)
        
        if existing.exists():
            raise ValidationError("Ya existe una categoría con este nombre.")
        
        return name.strip()

    def clean_color(self):
        color = self.cleaned_data.get('color')
        if color and not re.match(r'^#[0-9A-Fa-f]{6}$', color): # CORRECTED REGEX
            raise ValidationError("El color debe ser un código hexadecimal válido.")
        return color


class BulkActionForm(forms.Form):
    """Formulario para acciones en lote en posts"""
    
    ACTION_CHOICES = [
        ('publish', 'Publicar'),
        ('draft', 'Cambiar a borrador'),
        ('archive', 'Archivar'),
        ('delete', 'Eliminar'),
        ('feature', 'Marcar como destacado'),
        ('unfeature', 'Quitar destacado'),
    ]
    
    action = forms.ChoiceField(
        choices=ACTION_CHOICES,
        widget=forms.Select(attrs={'class': 'form-input form-select'})
    )
    
    posts = forms.ModelMultipleChoiceField(
        queryset=Post.objects.all(),
        widget=forms.CheckboxSelectMultiple()
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filtrar posts según permisos del usuario
        if user:
            if user.is_staff:
                self.fields['posts'].queryset = Post.objects.all()
            else:
                self.fields['posts'].queryset = Post.objects.filter(author=user)


# Formularios inline para admin
class CategoryInlineForm(forms.ModelForm):
    """Formulario inline para categorías en admin"""
    class Meta:
        model = Category
        fields = '__all__'
