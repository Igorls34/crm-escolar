import os
from pathlib import Path
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

# -------------------
# Segurança (produção)
# -------------------
SECRET_KEY = os.getenv('SECRET_KEY', '5b5df44c25f6dc1e9202eaa4dc6a706e')

# DEBUG via variável de ambiente; padrão False
DEBUG = os.getenv('DEBUG', 'False') == 'True'
# ALLOWED_HOSTS via variável de ambiente, separado por vírgulas
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '*').split(',')

# -------------------
# Apps instalados
# -------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core.apps.CoreConfig',  # Configuração explícita do app core
    'django.contrib.humanize',
]

# -------------------
# Middlewares
# -------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'crm_escolar.urls'

# -------------------
# Templates
# -------------------
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],  # Diretório de templates customizados
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'crm_escolar.wsgi.application'

# -------------------
# Banco de Dados
# -------------------
# Usa DATABASE_URL em produção; senão, SQLite local
if os.getenv('DATABASE_URL'):
    DATABASES = {
        'default': dj_database_url.config(conn_max_age=600, ssl_require=True)
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# -------------------
# Validação de senha
# -------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# -------------------
# Internacionalização
# -------------------
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

# -------------------
# Arquivos estáticos (CSS, JS, imagens)
# -------------------
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# -------------------
# Autenticação
# -------------------
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/leads/'
LOGOUT_REDIRECT_URL = '/login/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
