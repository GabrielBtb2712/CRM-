from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
SECRET_KEY = 'django-insecure-dm2_w2jc!8bh6g5n72n=-=c%8n2gd-4r!35utndaq3zfx@ag+h'
DEBUG = True
ALLOWED_HOSTS = ['*']

# Application definition
INSTALLED_APPS = [
    'api',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',  # Asegúrate de que esté incluida
    'storages',  # Para usar Google Cloud Storage
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'DJANGOAPPI.urls'

# Templates configuration
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'api', 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'DJANGOAPPI.wsgi.application'

# Database configuration (SQLite for development)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# Configuración de Google Cloud Storage para archivos estáticos
GS_BUCKET_NAME = 'nombre-de-tu-bucket'
GS_PROJECT_ID = 'tu-id-de-proyecto'  # Proyecto en Google Cloud
GS_CREDENTIALS = '/home/dragon/Descargas/hip-river-441601-p7-0581b2f9f162.json'  # Ruta al archivo de credenciales

STATIC_URL = f'https://storage.googleapis.com/{GS_BUCKET_NAME}/static/'  # Usar la URL pública de GCS para archivos estáticos
STATICFILES_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'  # Usar Google Cloud Storage para archivos estáticos

# Configuración de los archivos de media (si los usas también en el mismo bucket)
DEFAULT_FILE_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
GS_MEDIA_BUCKET_NAME = GS_BUCKET_NAME  # Si los archivos de medios también se almacenan en el mismo bucket

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


GS_CREDENTIALS = '/home/dragon/VS_code/PythonDjango/hip-river-441601-p7-0581b2f9f162.json'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
