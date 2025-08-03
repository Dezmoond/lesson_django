"""
Настройки для тестирования Django проекта
"""

from .settings import *

# Используем тестовую базу данных
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',  # Используем in-memory базу данных для быстрых тестов
    }
}

# Отключаем кэширование для тестов
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Настройки для тестирования email
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Отключаем логирование для тестов
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
}

# Настройки для тестирования медиа файлов
MEDIA_ROOT = '/tmp/test_media/'

# Настройки для тестирования статических файлов
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Отключаем отладку для тестов
DEBUG = False

# Секретный ключ для тестов
SECRET_KEY = 'test-secret-key-for-testing-only'

# Настройки для тестирования сессий
SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# Настройки для тестирования аутентификации
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
LOGIN_URL = '/users/login/'

# Отключаем middleware, которые могут замедлять тесты
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Настройки для тестирования шаблонов
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

# Настройки для тестирования локализации
USE_I18N = False
USE_L10N = False
USE_TZ = False

# Настройки для тестирования пагинации
PAGINATE_BY = 10

# Настройки для тестирования файлов
FILE_UPLOAD_HANDLERS = [
    'django.core.files.uploadhandler.MemoryFileUploadHandler',
    'django.core.files.uploadhandler.TemporaryFileUploadHandler',
]

# Максимальный размер загружаемого файла для тестов
DATA_UPLOAD_MAX_MEMORY_SIZE = 2621440  # 2.5 MB

# Настройки для тестирования безопасности
SECURE_BROWSER_XSS_FILTER = False
SECURE_CONTENT_TYPE_NOSNIFF = False
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_SECONDS = 0
SECURE_REDIRECT_EXEMPT = []
SECURE_SSL_REDIRECT = False
SECURE_PROXY_SSL_HEADER = None

# Настройки для тестирования CSRF
CSRF_COOKIE_SECURE = False
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SAMESITE = None
CSRF_TRUSTED_ORIGINS = []

# Настройки для тестирования сессий
SESSION_COOKIE_SECURE = False
SESSION_COOKIE_HTTPONLY = False
SESSION_COOKIE_SAMESITE = None
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_SAVE_EVERY_REQUEST = False

# Настройки для тестирования сообщений
MESSAGE_STORAGE = 'django.contrib.messages.storage.fallback.FallbackStorage'

# Настройки для тестирования статических файлов
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Настройки для тестирования медиа файлов
MEDIA_URL = '/media/'

# Настройки для тестирования приложений
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'postapp',
    'users',
]

# Настройки для тестирования URL
ROOT_URLCONF = 'blog.urls'

# Настройки для тестирования WSGI
WSGI_APPLICATION = 'blog.wsgi.application'

# Настройки для тестирования ASGI
ASGI_APPLICATION = 'blog.asgi.application'

# Настройки для тестирования пользовательской модели
AUTH_USER_MODEL = 'users.CustomUser'

# Настройки для тестирования админки
ADMIN_SITE_HEADER = "Тестовая админка"
ADMIN_SITE_TITLE = "Тестовая админка"
ADMIN_INDEX_TITLE = "Добро пожаловать в тестовую админку"

# Настройки для тестирования форм
FORM_RENDERER = 'django.forms.renderers.DjangoTemplates'

# Настройки для тестирования валидации
SILENCED_SYSTEM_CHECKS = [
    'django.security.W019',  # Отключаем предупреждения о безопасности для тестов
]

# Настройки для тестирования производительности
TEST_RUNNER = 'django.test.runner.DiscoverRunner'

# Настройки для тестирования покрытия кода
COVERAGE_MODULE_EXCLUDES = [
    'tests$',
    'settings$',
    'urls$',
    'wsgi$',
    'asgi$',
    'migrations$',
    '__pycache__$',
]

# Настройки для тестирования фикстур
FIXTURE_DIRS = [
    BASE_DIR / 'fixtures',
]

# Настройки для тестирования команд
MANAGEMENT_COMMANDS = [
    'parse_events',
]

# Настройки для тестирования API (если будет добавлен в будущем)
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
}

# Настройки для тестирования Celery (если будет добавлен в будущем)
CELERY_BROKER_URL = 'memory://'
CELERY_RESULT_BACKEND = 'rpc://'

# Настройки для тестирования Redis (если будет добавлен в будущем)
REDIS_URL = 'redis://localhost:6379/0'

# Настройки для тестирования PostgreSQL (если будет переключен в будущем)
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'test_db',
#         'USER': 'test_user',
#         'PASSWORD': 'test_password',
#         'HOST': 'localhost',
#         'PORT': '5432',
#     }
# }

# Настройки для тестирования MySQL (если будет переключен в будущем)
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'test_db',
#         'USER': 'test_user',
#         'PASSWORD': 'test_password',
#         'HOST': 'localhost',
#         'PORT': '3306',
#     }
# } 