from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ["localhost","127.0.0.1","api.securityforce.in","securityforce.in","frontend.securityforce.in", "194.195.114.190"]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

CORS_ALLOW_ALL_ORIGINS = True


GDAL_LIBRARY_PATH = r'C:\OSGeo4W\bin\gdal307'
GEOS_LIBRARY_PATH = r'C:\OSGeo4W\bin\geos_c.dll'

try:
    from .local import *
except ImportError:
    pass
