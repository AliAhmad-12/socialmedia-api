from pathlib import Path
import os



from dotenv import load_dotenv
load_dotenv()
import dj_database_url
BASE_DIR = Path(__file__).resolve().parent.parent




SECRET_KEY =str(os.getenv('SECRET_KEY'))

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['*']
CSRF_TRUSTED_ORIGINS=['https://social-media-api-with-django-rest-framework-and-channels.vercel.app']

# Application definition

INSTALLED_APPS = [
    'daphne',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    "whitenoise.runserver_nostatic",#for deploy
    'django.contrib.postgres',#for deploy

    'app',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'rest_framework',
    "corsheaders",

    'oauth2_provider',
    'social_django', # pip install social-auth-app-django
    # for channels
    'channels',



    
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'app.authentication.CookiesJWTAuthentication',
        'oauth2_provider.contrib.rest_framework.OAuth2Authentication' , 
        'drf_social_oauth2.authentication.SocialAuthentication' , 
    )
}

AUTHENTICATION_BACKENDS = ( 
    # Google OAuth2 
   'social_core.backends.google.GoogleOAuth2' , 
   'drf_social_oauth2.backends.DjangoOAuth2' , 
   'django.contrib.auth.backends.ModelBackend' , 
) 
SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE = [ 
    'https://www.googleapis.com/auth/userinfo.email' , 
    'https://www.googleapis.com/auth/userinfo.profile' , 
] 
AUTH_USER_MODEL='app.CustomUser'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    "whitenoise.middleware.WhiteNoiseMiddleware",
    'django.contrib.sessions.middleware.SessionMiddleware',
    "corsheaders.middleware.CorsMiddleware",    #new
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

]

ROOT_URLCONF = 'backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',

                'social_django.context_processors.backends' , 
                'social_django.context_processors.login_redirect' ,
            ],
        },
    },
]

WSGI_APPLICATION = 'backend.wsgi.application'
ASGI_APPLICATION = 'backend.asgi.application'

# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }
DATABSE_URL="postgresql://postgres:JZSGBTGVQIHQtHrrBkKaygHazOZCRYVw@turntable.proxy.rlwy.net:42103/railway"
DATABASES = {
'default':dj_database_url.config(default=DATABSE_URL,conn_max_age=500)
}

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Damascus'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT=os.path.join(BASE_DIR,'staticfiles_build','static')
# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'



from datetime import timedelta

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=2),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": False,
    "UPDATE_LAST_LOGIN": False,

    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "VERIFYING_KEY": "",
    "AUDIENCE": None,
    "ISSUER": None,
    "JSON_ENCODER": None,
    "JWK_URL": None,
    "LEEWAY": 0,

    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "USER_AUTHENTICATION_RULE": "rest_framework_simplejwt.authentication.default_user_authentication_rule",


}







CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "https://social-media-v1.vercel.app"
]
CORS_ALLOW_CREDENTIALS = True


MEDIA_URL='/media/'
MEDIA_ROOT=os.path.join(BASE_DIR,'media')

INTERNAL_IPS="127.0.0.1"

GOOGLE_OAUTH_REDIRECT_URI='http://localhost:3000/google/callback/'
GOOGLE_OAUTH_CLIENT_ID=str(os.getenv('GOOGLE_OAUTH_CLIENT_ID'))
GOOGLE_OAUTH_CLIENT_SECRET=str(os.getenv('GOOGLE_OAUTH_CLIENT_SECRET'))


ACCOUNT_AUTHENTICATION_METHOD = "email"  # Use Email / Password authentication
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = "none" # Do not require email confirmation


# CHANNEL_LAYERS = {
#     'default': {
#         'BACKEND': 'channels_redis.core.RedisChannelLayer',
#         'CONFIG': {
#             "hosts": [('127.0.0.1', 6379)],
#         },
#     },
# }

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [('redis://default:bllrnAUNReucSRvRUnaeuifPqknJrQGs@gondola.proxy.rlwy.net:53978')],
        },
    },
}
