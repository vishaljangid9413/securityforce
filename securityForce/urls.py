"""
URL configuration for securityForce project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from accounts import urls as accountsURLs
from location import urls as locationURLs
from business import urls as businessURLs
from officer import urls as officerURLs
from tracking import urls as trackingURLs
from communication import urls as communicationURLs
from content import urls as contentURLs
from report import urls as reportURLs
from ecommerce import urls as ecommerceURLs
from master import urls as masterURLs

admin.site.site_title = "SecurityForce Admin"
admin.site.index_title = "Dashboard"
admin.site.site_header = "Security Force"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(accountsURLs)),
    path('', include(locationURLs)),
    path('', include(businessURLs)),
    path('', include(officerURLs)),
    path('', include(trackingURLs)),
    path('', include(communicationURLs)),
    path('', include(contentURLs)),
    path('', include(contentURLs)),
    path('', include(reportURLs)),
    path('', include(ecommerceURLs)),
    path('', include(masterURLs)),

    # path('api/rest-auth/password/reset/', CustomPasswordResetView.as_view(), name='rest_password_reset'),
    # re_path('api/password/reset/confirm/(?P<uidb64>[0-9A-Za-z]+)/(?P<token>.+)/$', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('api/rest-auth/', include('dj_rest_auth.urls')),
    # path('api/rest-auth/registration/', include('dj_rest_auth.urls.registration.urls')),
]

if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
