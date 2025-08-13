// ==============================================
// POSTS JAVASCRIPT - The Caffeine Lane
// ==============================================

document.addEventListener('DOMContentLoaded', function() {
    
    // ==============================================
    // CONFIGURACIÓN GLOBAL
    // ==============================================
    
    const ANIMATION_DELAY = 100;
    const DEBOUNCE_DELAY = 300;
    
    // ==============================================
    // ANIMACIONES DE ENTRADA
    // ==============================================
    
    function initializeAnimations() {
        const animatedElements = document.querySelectorAll('.post-card, .comment, .post-detail');
        
        animatedElements.forEach((element, index) => {
            element.style.opacity = '0';
            element.style.transform = 'translateY(20px)';
            
            setTimeout(() => {
                element.style.transition = 'all 0.6s ease';
                element.style.opacity = '1';
                element.style.transform = 'translateY(0)';
            }, index * ANIMATION_DELAY);
        });
    }
    
    // ==============================================
    // FORMULARIO DE POSTS - VALIDACIÓN Y UX
    // ==============================================
    
    const postForm = document.querySelector('#post-form');
    if (postForm) {
        initializePostForm(postForm);
    }
    
    function initializePostForm(form) {
        const titleInput = form.querySelector('input[name="title"]');
        const contentTextarea = form.querySelector('textarea[name="content"]');
        const imageInput = form.querySelector('input[name="image"]');
        const categoriesSelect = form.querySelector('select[name="categories"]');
        const submitBtn = form.querySelector('.btn-form-submit');
        
        // Validación en tiempo real del título
        if (titleInput) {
            titleInput.addEventListener('input', function() {
                validateTitle(this);
                updateSlugPreview(this.value);
            });
        }
        
        // Contador de caracteres para contenido
        if (contentTextarea) {
            setupCharacterCounter(contentTextarea);
            setupAutoResize(contentTextarea);
        }
        
        // Validación de imagen
        if (imageInput) {
            imageInput.addEventListener('change', function() {
                validateImage(this);
            });
        }
        
        // Validación del formulario completo
        form.addEventListener('submit', function(e) {
            if (!validatePostForm(form)) {
                e.preventDefault();
                showFormMessage('Por favor, corrige los errores antes de continuar.', 'error');
            } else {
                showLoadingState(submitBtn);
            }
        });
        
        // Auto-guardado (draft)
        setupAutoSave(form);
    }
    
    function validateTitle(input) {
        const value = input.value.trim();
        const minLength = 5;
        const maxLength = 200;
        
        clearFieldError(input);
        
        if (value.length < minLength) {
            showFieldError(input, `El título debe tener al menos ${minLength} caracteres.`);
            return false;
        }
        
        if (value.length > maxLength) {
            showFieldError(input, `El título no puede exceder ${maxLength} caracteres.`);
            return false;
        }
        
        return true;
    }
    
    function validateImage(input) {
        const file = input.files[0];
        if (!file) return true;
        
        const maxSize = 5 * 1024 * 1024; // 5MB
        const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'];
        
        clearFieldError(input);
        
        if (file.size > maxSize) {
            showFieldError(input, 'La imagen debe ser menor a 5MB.');
            input.value = '';
            return false;
        }
        
        if (!allowedTypes.includes(file.type)) {
            showFieldError(input, 'Solo se permiten archivos de imagen (JPG, PNG, GIF, WebP).');
            input.value = '';
            return false;
        }
        
        // Vista previa de la imagen
        showImagePreview(file, input);
        return true;
    }
    
    function showImagePreview(file, input) {
        const reader = new FileReader();
        reader.onload = function(e) {
            let preview = document.querySelector('.image-preview');
            if (!preview) {
                preview = document.createElement('div');
                preview.className = 'image-preview';
                input.parentNode.appendChild(preview);
            }
            
            preview.innerHTML = `
                <img src="${e.target.result}" alt="Vista previa" style="max-width: 200px; max-height: 200px; border-radius: 8px; margin-top: 1rem;">
                <button type="button" class="remove-preview" onclick="removeImagePreview()">
                    <i class="fas fa-times"></i>
                </button>
            `;
        };
        reader.readAsDataURL(file);
    }
    
    function setupCharacterCounter(textarea) {
        const maxLength = 5000;
        const counter = document.createElement('div');
        counter.className = 'character-counter';
        counter.style.textAlign = 'right';
        counter.style.fontSize = '0.75rem';
        counter.style.color = '#6b7280';
        counter.style.marginTop = '0.5rem';
        
        textarea.parentNode.appendChild(counter);
        
        function updateCounter() {
            const remaining = maxLength - textarea.value.length;
            counter.textContent = `${remaining} caracteres restantes`;
            
            if (remaining < 100) {
                counter.style.color = '#dc2626';
            } else if (remaining < 500) {
                counter.style.color = '#f59e0b';
            } else {
                counter.style.color = '#6b7280';
            }
        }
        
        updateCounter();
        textarea.addEventListener('input', updateCounter);
    }
    
    function setupAutoResize(textarea) {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight + 2) + 'px';
        });
    }
    
    function updateSlugPreview(title) {
        const slugPreview = document.querySelector('.slug-preview');
        if (!slugPreview) return;
        
        const slug = title.toLowerCase()
            .trim()
            .replace(/[^\w\s-]/g, '')
            .replace(/[\s_-]+/g, '-')
            .replace(/^-+|-+$/g, '');
        
        slugPreview.textContent = slug || 'titulo-del-post';
    }
    
    function setupAutoSave(form) {
        let autoSaveTimeout;
        const inputs = form.querySelectorAll('input, textarea, select');
        
        inputs.forEach(input => {
            input.addEventListener('input', function() {
                clearTimeout(autoSaveTimeout);
                autoSaveTimeout = setTimeout(() => {
                    saveAsDraft(form);
                }, 5000); // Auto-guardar cada 5 segundos de inactividad
            });
        });
    }
    
    function saveAsDraft(form) {
        const formData = new FormData(form);
        formData.set('status', 'draft');
        
        // Aquí iría la lógica de auto-guardado via AJAX
        console.log('Auto-guardando borrador...');
    }
    
    // ==============================================
    // COMENTARIOS - FUNCIONALIDAD INTERACTIVA
    // ==============================================
    
    const commentForm = document.querySelector('#comment-form');
    if (commentForm) {
        initializeCommentForm(commentForm);
    }
    
    function initializeCommentForm(form) {
        const textarea = form.querySelector('textarea[name="content"]');
        const submitBtn = form.querySelector('.btn-form-submit');
        
        if (textarea) {
            setupCharacterCounter(textarea, 500);
            setupAutoResize(textarea);
        }
        
        form.addEventListener('submit', function(e) {
            if (!validateCommentForm(form)) {
                e.preventDefault();
            } else {
                showLoadingState(submitBtn);
            }
        });
    }
    
    function validateCommentForm(form) {
        const textarea = form.querySelector('textarea[name="content"]');
        const content = textarea.value.trim();
        
        clearFieldError(textarea);
        
        if (content.length < 3) {
            showFieldError(textarea, 'El comentario debe tener al menos 3 caracteres.');
            return false;
        }
        
        if (content.length > 500) {
            showFieldError(textarea, 'El comentario no puede exceder 500 caracteres.');
            return false;
        }
        
        return true;
    }
    
    // Responder a comentarios
    function replyToComment(commentId) {
        const commentForm = document.querySelector('#comment-form');
        if (!commentForm) return;
        
        const parentInput = commentForm.querySelector('input[name="parent"]');
        if (parentInput) {
            parentInput.value = commentId;
        }
        
        const textarea = commentForm.querySelector('textarea');
        if (textarea) {
            textarea.focus();
            textarea.placeholder = 'Escribe tu respuesta...';
        }
        
        // Mostrar indicador de respuesta
        showReplyIndicator(commentId);
    }
    
    function showReplyIndicator(commentId) {
        // Remover indicador previo
        const prevIndicator = document.querySelector('.reply-indicator');
        if (prevIndicator) prevIndicator.remove();
        
        const comment = document.querySelector(`[data-comment-id="${commentId}"]`);
        if (!comment) return;
        
        const indicator = document.createElement('div');
        indicator.className = 'reply-indicator';
        indicator.innerHTML = `
            <span>Respondiendo a ${comment.querySelector('.comment-author-name').textContent}</span>
            <button type="button" onclick="cancelReply()">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        const commentForm = document.querySelector('#comment-form');
        commentForm.insertBefore(indicator, commentForm.firstChild);
    }
    
    function cancelReply() {
        const parentInput = document.querySelector('input[name="parent"]');
        if (parentInput) parentInput.value = '';
        
        const textarea = document.querySelector('#comment-form textarea');
        if (textarea) textarea.placeholder = 'Escribe tu comentario...';
        
        const indicator = document.querySelector('.reply-indicator');
        if (indicator) indicator.remove();
    }
    
    // ==============================================
    // BÚSQUEDA Y FILTROS
    // ==============================================
    
    const searchInput = document.querySelector('#search-input');
    const categoryFilter = document.querySelector('#category-filter');
    const sortFilter = document.querySelector('#sort-filter');
    
    if (searchInput) {
        searchInput.addEventListener('input', debounce(performSearch, DEBOUNCE_DELAY));
    }
    
    if (categoryFilter) {
        categoryFilter.addEventListener('change', applyFilters);
    }
    
    if (sortFilter) {
        sortFilter.addEventListener('change', applyFilters);
    }
    
    function performSearch() {
        const query = searchInput.value.trim();
        const category = categoryFilter ? categoryFilter.value : '';
        const sort = sortFilter ? sortFilter.value : '';
        
        // Construir URL con parámetros
        const url = new URL(window.location);
        
        if (query) {
            url.searchParams.set('search', query);
        } else {
            url.searchParams.delete('search');
        }
        
        if (category) {
            url.searchParams.set('category', category);
        } else {
            url.searchParams.delete('category');
        }
        
        if (sort) {
            url.searchParams.set('sort', sort);
        } else {
            url.searchParams.delete('sort');
        }
        
        // Remover paginación al filtrar
        url.searchParams.delete('page');
        
        // Recargar página con nuevos filtros
        window.location.href = url.toString();
    }
    
    function applyFilters() {
        performSearch();
    }
    
    // ==============================================
    // CONFIRMACIONES DE ELIMINACIÓN
    // ==============================================
    
    const deleteButtons = document.querySelectorAll('.btn-delete, .delete-post, .delete-comment');
    deleteButtons.forEach(btn => {
        btn.addEventListener('click', function(e) {
            if (!confirm('¿Estás seguro de que quieres eliminar este elemento? Esta acción no se puede deshacer.')) {
                e.preventDefault();
            }
        });
    });
    
    // ==============================================
    // LAZY LOADING DE IMÁGENES
    // ==============================================
    
    function initializeLazyLoading() {
        const images = document.querySelectorAll('img[data-src]');
        
        if ('IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        img.src = img.dataset.src;
                        img.classList.remove('lazy');
                        imageObserver.unobserve(img);
                    }
                });
            });
            
            images.forEach(img => imageObserver.observe(img));
        } else {
            // Fallback para navegadores antiguos
            images.forEach(img => {
                img.src = img.dataset.src;
            });
        }
    }
    
    // ==============================================
    // COMPARTIR EN REDES SOCIALES
    // ==============================================
    
    function sharePost(platform, url, title) {
        const encodedUrl = encodeURIComponent(url);
        const encodedTitle = encodeURIComponent(title);
        let shareUrl = '';
        
        switch (platform) {
            case 'twitter':
                shareUrl = `https://twitter.com/intent/tweet?url=${encodedUrl}&text=${encodedTitle}`;
                break;
            case 'facebook':
                shareUrl = `https://www.facebook.com/sharer/sharer.php?u=${encodedUrl}`;
                break;
            case 'linkedin':
                shareUrl = `https://www.linkedin.com/sharing/share-offsite/?url=${encodedUrl}`;
                break;
            case 'whatsapp':
                shareUrl = `https://wa.me/?text=${encodedTitle} ${encodedUrl}`;
                break;
        }
        
        if (shareUrl) {
            window.open(shareUrl, '_blank', 'width=600,height=400');
        }
    }
    
    // ==============================================
    // FUNCIONES DE UTILIDAD
    // ==============================================
    
    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
    
    function showFieldError(field, message) {
        clearFieldError(field);
        
        field.classList.add('error');
        
        const errorDiv = document.createElement('div');
        errorDiv.className = 'form-error';
        errorDiv.textContent = message;
        
        field.parentNode.appendChild(errorDiv);
    }
    
    function clearFieldError(field) {
        field.classList.remove('error');
        
        const existingError = field.parentNode.querySelector('.form-error');
        if (existingError) {
            existingError.remove();
        }
    }
    
    function showFormMessage(message, type = 'info') {
        const messageDiv = document.createElement('div');
        messageDiv.className = `form-message form-message-${type}`;
        messageDiv.innerHTML = `
            <span>${message}</span>
            <button type="button" onclick="this.parentNode.remove()">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        const form = document.querySelector('form');
        if (form) {
            form.insertBefore(messageDiv, form.firstChild);
            
            // Auto-remover después de 5 segundos
            setTimeout(() => {
                if (messageDiv.parentNode) {
                    messageDiv.remove();
                }
            }, 5000);
        }
    }
    
    function showLoadingState(button) {
        if (!button) return;
        
        const originalText = button.textContent;
        button.disabled = true;
        button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Procesando...';
        
        // Restaurar después de 15 segundos (por si hay error)
        setTimeout(() => {
            button.disabled = false;
            button.textContent = originalText;
        }, 15000);
    }
    
    function validatePostForm(form) {
        const title = form.querySelector('input[name="title"]');
        const content = form.querySelector('textarea[name="content"]');
        let isValid = true;
        
        if (title && !validateTitle(title)) {
            isValid = false;
        }
        
        if (content) {
            const contentValue = content.value.trim();
            clearFieldError(content);
            
            if (contentValue.length < 10) {
                showFieldError(content, 'El contenido debe tener al menos 10 caracteres.');
                isValid = false;
            }
        }
        
        return isValid;
    }
    
    // ==============================================
    // FUNCIONES GLOBALES PARA USO EN TEMPLATES
    // ==============================================
    
    window.replyToComment = replyToComment;
    window.cancelReply = cancelReply;
    window.sharePost = sharePost;
    window.removeImagePreview = function() {
        const preview = document.querySelector('.image-preview');
        const input = document.querySelector('input[name="image"]');
        if (preview) preview.remove();
        if (input) input.value = '';
    };
    
    // ==============================================
    // INICIALIZACIÓN
    // ==============================================
    
    initializeAnimations();
    initializeLazyLoading();
    
    // Mostrar mensaje de confirmación si existe
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('success')) {
        showFormMessage('Operación completada exitosamente.', 'success');
    }
    
    console.log('Posts JavaScript initialized successfully');
});