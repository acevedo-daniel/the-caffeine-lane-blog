// ==============================================
// ACCOUNTS JAVASCRIPT - The Caffeine Lane
// ==============================================

document.addEventListener('DOMContentLoaded', function() {
    
    // ==============================================
    // FORMULARIO DE REGISTRO - VALIDACIONES
    // ==============================================
    const registerForm = document.querySelector('#register-form');
    if (registerForm) {
        
        // Validación en tiempo real
        const inputs = registerForm.querySelectorAll('input[type="text"], input[type="email"], input[type="password"]');
        
        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                validateField(this);
            });
            
            input.addEventListener('input', function() {
                clearFieldError(this);
            });
        });
        
        // Validación de contraseñas coincidentes
        const password1 = registerForm.querySelector('input[name="password1"]');
        const password2 = registerForm.querySelector('input[name="password2"]');
        
        if (password1 && password2) {
            password2.addEventListener('blur', function() {
                validatePasswordMatch(password1, password2);
            });
        }
        
        // Envío del formulario
        registerForm.addEventListener('submit', function(e) {
            let isValid = true;
            
            inputs.forEach(input => {
                if (!validateField(input)) {
                    isValid = false;
                }
            });
            
            if (password1 && password2) {
                if (!validatePasswordMatch(password1, password2)) {
                    isValid = false;
                }
            }
            
            if (!isValid) {
                e.preventDefault();
                showMessage('Por favor, corrige los errores antes de continuar.', 'error');
            } else {
                showLoadingButton(this.querySelector('button[type="submit"]'));
            }
        });
    }
    
    // ==============================================
    // FORMULARIO DE LOGIN
    // ==============================================
    const loginForm = document.querySelector('#login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            const submitBtn = this.querySelector('button[type="submit"]');
            showLoadingButton(submitBtn);
        });
    }
    
    // ==============================================
    // ANIMACIONES DE ENTRADA
    // ==============================================
    const authElements = document.querySelectorAll('.auth-container, .register-container, .auth-btn-primary, .message-success, .message-error, .message-info');
    authElements.forEach((element, index) => {
        element.style.opacity = '0';
        element.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            element.style.transition = 'all 0.6s ease';
            element.style.opacity = '1';
            element.style.transform = 'translateY(0)';
        }, index * 100);
    });
    
    // ==============================================
    // FUNCIONES DE VALIDACIÓN
    // ==============================================
    
    function validateField(field) {
        const value = field.value.trim();
        const fieldName = field.name;
        let isValid = true;
        let errorMessage = '';
        
        // Limpiar errores previos
        clearFieldError(field);
        
        // Validaciones específicas por tipo de campo
        switch(fieldName) {
            case 'email':
                if (!value) {
                    errorMessage = 'El email es requerido.';
                    isValid = false;
                } else if (!isValidEmail(value)) {
                    errorMessage = 'Ingresa un email válido.';
                    isValid = false;
                }
                break;
                
            case 'username':
                if (!value) {
                    errorMessage = 'El nombre de usuario es requerido.';
                    isValid = false;
                } else if (value.length < 3) {
                    errorMessage = 'El nombre de usuario debe tener al menos 3 caracteres.';
                    isValid = false;
                } else if (!/^[a-zA-Z0-9_]+$/.test(value)) {
                    errorMessage = 'Solo se permiten letras, números y guiones bajos.';
                    isValid = false;
                }
                break;
                
            case 'password1':
                if (!value) {
                    errorMessage = 'La contraseña es requerida.';
                    isValid = false;
                } else if (value.length < 8) {
                    errorMessage = 'La contraseña debe tener al menos 8 caracteres.';
                    isValid = false;
                } else if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(value)) {
                    errorMessage = 'Debe contener al menos una mayúscula, una minúscula y un número.';
                    isValid = false;
                }
                break;
                
            case 'first_name':
            case 'last_name':
                if (!value) {
                    errorMessage = 'Este campo es requerido.';
                    isValid = false;
                } else if (!/^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$/.test(value)) {
                    errorMessage = 'Solo se permiten letras y espacios.';
                    isValid = false;
                }
                break;
        }
        
        if (!isValid) {
            showFieldError(field, errorMessage);
        }
        
        return isValid;
    }
    
    function validatePasswordMatch(password1, password2) {
        if (password1.value !== password2.value) {
            showFieldError(password2, 'Las contraseñas no coinciden.');
            return false;
        }
        clearFieldError(password2);
        return true;
    }
    
    function isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }
    
    // ==============================================
    // FUNCIONES DE UI
    // ==============================================
    
    function showFieldError(field, message) {
        clearFieldError(field);
        
        field.classList.add('border-red-500');
        
        const errorDiv = document.createElement('div');
        errorDiv.className = 'field-error';
        errorDiv.textContent = message;
        
        field.parentNode.appendChild(errorDiv);
    }
    
    function clearFieldError(field) {
        field.classList.remove('border-red-500');
        
        const existingError = field.parentNode.querySelector('.field-error');
        if (existingError) {
            existingError.remove();
        }
    }
    
    function showMessage(message, type = 'info') {
        // Crear el elemento del mensaje
        const messageDiv = document.createElement('div');
        messageDiv.className = `message-${type}`;
        messageDiv.textContent = message;
        
        // Insertar al principio del formulario
        const form = document.querySelector('form');
        if (form) {
            form.insertBefore(messageDiv, form.firstChild);
        }
        
        // Auto-eliminar después de 5 segundos
        setTimeout(() => {
            if (messageDiv.parentNode) {
                messageDiv.remove();
            }
        }, 5000);
    }
    
    function showLoadingButton(button) {
        if (!button) return;
        
        const originalText = button.innerHTML;
        button.disabled = true;
        button.innerHTML = '<span class="auth-loading"></span> Procesando...';
        
        // Restaurar después de 10 segundos (por si hay error de red)
        setTimeout(() => {
            button.disabled = false;
            button.innerHTML = originalText;
        }, 10000);
    }
    
    // ==============================================
    // MEJORAR UX DE RADIO BUTTONS
    // ==============================================
    const radioButtons = document.querySelectorAll('input[type="radio"]');
    radioButtons.forEach(radio => {
        radio.addEventListener('change', function() {
            // Efecto visual al seleccionar
            const label = this.nextElementSibling || this.parentNode.querySelector('label');
            if (label) {
                label.style.transform = 'scale(1.05)';
                setTimeout(() => {
                    label.style.transform = '';
                }, 150);
            }
        });
    });
    
    // ==============================================
    // VALIDACIÓN DE ARCHIVOS (AVATAR)
    // ==============================================
    const avatarInput = document.querySelector('input[type="file"][name="avatar"]');
    if (avatarInput) {
        avatarInput.addEventListener('change', function() {
            const file = this.files[0];
            if (file) {
                // Validar tamaño (máximo 5MB)
                if (file.size > 5 * 1024 * 1024) {
                    showMessage('El archivo debe ser menor a 5MB.', 'error');
                    this.value = '';
                    return;
                }
                
                // Validar tipo
                const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif'];
                if (!allowedTypes.includes(file.type)) {
                    showMessage('Solo se permiten archivos de imagen (JPG, PNG, GIF).', 'error');
                    this.value = '';
                    return;
                }
                
                // Vista previa (opcional)
                const reader = new FileReader();
                reader.onload = function(e) {
                    const preview = document.querySelector('.profile-avatar');
                    if (preview) {
                        preview.style.backgroundImage = `url(${e.target.result})`;
                        preview.style.backgroundSize = 'cover';
                        preview.style.backgroundPosition = 'center';
                    }
                };
                reader.readAsDataURL(file);
            }
        });
    }
    
    // ==============================================
    // CONTADOR DE CARACTERES PARA BIO
    // ==============================================
    const bioTextarea = document.querySelector('textarea[name="bio"]');
    if (bioTextarea) {
        const maxLength = 500;
        
        // Crear contador
        const counterDiv = document.createElement('div');
        counterDiv.className = 'text-gray-400 text-xs mt-1 text-right';
        bioTextarea.parentNode.appendChild(counterDiv);
        
        function updateCounter() {
            const remaining = maxLength - bioTextarea.value.length;
            counterDiv.textContent = `${remaining} caracteres restantes`;
            
            if (remaining < 50) {
                counterDiv.className = 'text-red-400 text-xs mt-1 text-right';
            } else {
                counterDiv.className = 'text-gray-400 text-xs mt-1 text-right';
            }
        }
        
        updateCounter();
        bioTextarea.addEventListener('input', updateCounter);
    }
    
    // ==============================================
    // AUTO-DISMISS DE MENSAJES
    // ==============================================
    const messages = document.querySelectorAll('.message-success, .message-error, .message-info');
    messages.forEach(message => {
        // Añadir botón de cerrar
        const closeBtn = document.createElement('button');
        closeBtn.innerHTML = '×';
        closeBtn.className = 'ml-2 text-xl font-bold opacity-70 hover:opacity-100';
        closeBtn.onclick = () => message.remove();
        message.appendChild(closeBtn);
        
        // Auto-eliminar después de 8 segundos
        setTimeout(() => {
            if (message.parentNode) {
                message.style.opacity = '0';
                message.style.transform = 'translateY(-10px)';
                setTimeout(() => message.remove(), 300);
            }
        }, 8000);
    });
});

// ==============================================
// FUNCIONES GLOBALES ÚTILES
// ==============================================

// Función para mostrar/ocultar contraseña
function togglePassword(inputId) {
    const input = document.getElementById(inputId);
    const icon = event.target;
    
    if (input.type === 'password') {
        input.type = 'text';
        icon.classList.remove('fa-eye');
        icon.classList.add('fa-eye-slash');
    } else {
        input.type = 'password';
        icon.classList.remove('fa-eye-slash');
        icon.classList.add('fa-eye');
    }
}

// Función para copiar al portapapeles
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showMessage('Copiado al portapapeles!', 'success');
    });
}