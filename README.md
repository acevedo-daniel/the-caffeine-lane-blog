# TheCaffeineLane - Proyecto Django

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Django](https://img.shields.io/badge/django-5.2-green)

---

## Tabla de Contenidos
- [¿Qué es este proyecto?](#qué-es-este-proyecto)
- [Estructura del proyecto](#estructura-del-proyecto)
- [¿Qué significa cada carpeta/archivo?](#qué-significa-cada-carpetaarchivo)
- [Cómo trabajar en este proyecto](#cómo-trabajar-en-este-proyecto)
- [Ejemplo de uso](#ejemplo-de-uso)
- [Variables de entorno](#variables-de-entorno)
- [Ejecutar tests](#ejecutar-tests)
- [Despliegue](#despliegue)
- [Buenas prácticas](#buenas-prácticas)
- [Licencia](#licencia)
- [Contacto y colaboración](#contacto-y-colaboración)

---

## ¿Qué es este proyecto?
Este es un proyecto base profesional en Django para un blog de motos tipo café racer. Está preparado para escalar y seguir las mejores prácticas de la industria.

---

## Estructura del proyecto

```
thecaffeinelane/
│
├── apps/
│   └── posts/
│       ├── __init__.py
│       ├── admin.py
│       ├── apps.py
│       ├── forms.py
│       ├── migrations/
│       │   └── __init__.py
│       ├── models.py
│       ├── tests.py
│       ├── urls.py
│       ├── views.py
│       └── templates/
│           └── posts/
│               └── (aquí irán tus templates)
│
├── config/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── manage.py
├── venv/
├── static/
├── media/
└── templates/
```

---

## ¿Qué significa cada carpeta/archivo?

- **apps/**: Aquí van todas las apps personalizadas del proyecto. Cada app es un módulo independiente (por ejemplo, `posts`).
- **apps/posts/**: App principal para gestionar publicaciones (posts) del blog.
  - `models.py`: Define las estructuras de datos (tablas de la base de datos).
  - `views.py`: Lógica de lo que se muestra al usuario.
  - `urls.py`: Rutas propias de la app.
  - `admin.py`: Configuración para el panel de administración.
  - `forms.py`: Formularios personalizados.
  - `templates/posts/`: Plantillas HTML específicas de la app.
  - `migrations/`: Archivos de migración de la base de datos.
- **config/**: Configuración principal del proyecto Django.
  - `settings.py`: Configuración global (apps, base de datos, rutas, etc).
  - `urls.py`: Rutas principales del proyecto.
- **manage.py**: Script para ejecutar comandos de Django (migraciones, servidor, etc).
- **venv/**: Entorno virtual de Python (no subir a git).
- **static/**: Archivos estáticos globales (CSS, JS, imágenes).
- **media/**: Archivos subidos por los usuarios.
- **templates/**: Plantillas HTML globales (base.html, errores, etc).

---

## ¿Cómo trabajar en este proyecto?

### 1. Clona el repositorio y entra a la carpeta del proyecto
```bash
git clone <url-del-repo>
cd thecaffeinelane
```

### 2. Crea y activa el entorno virtual
```bash
python -m venv venv
# En Windows (PowerShell):
venv\Scripts\Activate
# En Mac/Linux:
source venv/bin/activate
```

### 3. Instala las dependencias
```bash
pip install django
```

### 4. Aplica migraciones y crea un superusuario
```bash
python manage.py migrate
python manage.py createsuperuser
```

### 5. Ejecuta el servidor de desarrollo
```bash
python manage.py runserver
```

### 6. Estructura recomendada para nuevas apps
- Crea nuevas apps dentro de la carpeta `apps/`.
- Regístralas en `INSTALLED_APPS` en `config/settings.py` como `'apps.nueva_app'`.
- Crea sus propias carpetas de templates y archivos estándar (`forms.py`, `urls.py`, etc).

---

## Ejemplo de uso

### Crear un post desde el admin
1. Accede a `http://localhost:8000/admin/`.
2. Inicia sesión con tu superusuario.
3. Haz clic en "Posts" y luego en "Add post" para crear una nueva publicación.

### Mostrar posts en una vista (ejemplo básico)
```python
# apps/posts/views.py
from django.shortcuts import render
from .models import Post

def post_list(request):
    posts = Post.objects.all()
    return render(request, 'posts/post_list.html', {'posts': posts})
```

---

## Variables de entorno

Crea un archivo `.env` en la raíz del proyecto para variables sensibles (no lo subas a git):
```
SECRET_KEY=tu_clave_secreta
DEBUG=True
```

Puedes usar librerías como `python-dotenv` o `django-environ` para cargar estas variables en `settings.py`.

---

## Ejecutar tests

Para correr los tests automáticos:
```bash
python manage.py test
```

---

## Despliegue

- Para producción, pon `DEBUG = False` y configura `ALLOWED_HOSTS` en `config/settings.py`.
- Usa un servidor WSGI como Gunicorn o despliega en servicios como Heroku, Render, etc.
- Sirve archivos estáticos y media correctamente (consulta la [documentación oficial](https://docs.djangoproject.com/en/5.2/howto/deployment/)).

---

## Buenas prácticas
- Usa siempre entorno virtual.
- No subas `venv/`, `__pycache__/`, ni archivos sensibles a git.
- Mantén cada app independiente y modular.
- Usa migraciones para cambios en la base de datos.
- Documenta tus modelos, vistas y formularios.
- Haz commits frecuentes y descriptivos.
- Comenta tu código para que otros lo entiendan.

---

## Licencia

Este proyecto está bajo la licencia MIT. Puedes usarlo, modificarlo y compartirlo libremente.

---

## Contacto y colaboración

¿Tienes dudas o quieres contribuir?
- Lee la documentación oficial de Django: https://docs.djangoproject.com/es/5.2/
- Abre un issue o pull request en este repositorio.
- Contacta a los responsables del proyecto o pregunta en el equipo.

¡Colabora, aprende y diviértete programando en Django! 