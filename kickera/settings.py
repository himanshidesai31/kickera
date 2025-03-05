"""
Django settings for kickera project.
"""

from pathlib import Path

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-s_n828=qw_=07&b!loo+&u_@4v0+a)!6)i6+pdc6mnowvkezlm'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Allowed hosts
ALLOWED_HOSTS = ["*"]

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    # Project apps
    'orders',
    'core',
    'payment',
    'product',
    'users',
    'vendor',

    # Django-Allauth authentication system
    'django.contrib.humanize',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',

    'crispy_forms'
]
CRISPY_TEMPLATE_PACK = 'bootstrap4'

# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

ROOT_URLCONF = 'kickera.urls'

# Templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],  # Ensure custom templates are loaded
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


WSGI_APPLICATION = 'kickera.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Authentication Backends
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',  # Admin login
    'allauth.account.auth_backends.AuthenticationBackend',  # Allauth login
]

# Site ID (Required for Django-Allauth)
SITE_ID = 1

# Django-Allauth Configuration
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
# ACCOUNT_AUTHENTICATION_METHOD = 'email'
#upadated
ACCOUNT_LOGIN_METHODS = {'email'}  # Example value
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_SIGNUP_REDIRECT_URL = '/'  # Redirect after signup
LOGIN_REDIRECT_URL = '/' #redirect after login


# Password Validators
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

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


#static file
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

#media file
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default Primary Key Field Type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

#email configration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'chaudharykamlesh185@gmail.com'
EMAIL_HOST_PASSWORD = 'ejxwnmlcknlsfrqq'  # Use an App Password, NOT your Gmail password!,create app and there password paste here
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

#csrf token related configration
CSRF_TRUSTED_ORIGINS = ["http://localhost:8000", "http://127.0.0.1:8000"]
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]
CORS_ORIGIN_WHITELIST = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]


ACCOUNT_ADAPTER = 'allauth.account.adapter.DefaultAccountAdapter'
ACCOUNT_AUTHENTICATED_LOGIN_REDIRECTS = True
ACCOUNT_EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL = None
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 7


ACCOUNT_FORMS = {
    'signup': 'allauth.account.forms.SignupForm',
    'login': 'allauth.account.forms.LoginForm',
    'add_email': 'allauth.account.forms.AddEmailForm',
    'change_email': 'allauth.account.forms.ChangeEmailForm',
    'reset_password': 'allauth.account.forms.ResetPasswordForm',
    'change_password': 'allauth.account.forms.ChangePasswordForm',
    'confirm_email': 'allauth.account.forms.ConfirmEmailForm',
    'confirm_registration': 'allauth.account.forms.ConfirmRegistrationForm',
    'confirm_login': 'allauth.account.forms.ConfirmLoginForm',
    'confirm_login_code': 'allauth.account.forms.ConfirmLoginCodeForm',
    'request_login_code': 'allauth.account.forms.RequestLoginCodeForm',
    'reset_password_from_key': 'allauth.account.forms.ResetPasswordKeyForm',
}

AUTH_USER_MODEL = "users.User"