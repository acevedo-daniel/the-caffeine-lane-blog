# TheCaffeineLane - Proyecto Django

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

## Lógica general del flujo Django

1. El usuario accede a una URL.
2. Django busca la URL en `config/urls.py` y la redirige a la app correspondiente.
3. La app gestiona la lógica en `views.py` y obtiene datos de `models.py`.
4. Se renderiza un template HTML y se muestra al usuario.
5. El admin permite gestionar los datos desde una interfaz web.

---

## Buenas prácticas
- Usa siempre entorno virtual.
- No subas `venv/`, `__pycache__/`, ni archivos sensibles a git.
- Mantén cada app independiente y modular.
- Usa migraciones para cambios en la base de datos.
- Documenta tus modelos, vistas y formularios.

---

¿Dudas? ¡Lee la documentación oficial de Django o pregunta a tu equipo! 