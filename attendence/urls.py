from django.contrib import admin
from django.urls import path
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from attendence_hub.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', login,name="login"),
    path('attendence_hub/', include('attendence_hub.urls')),
]

urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL,document_root=settings.STATIC_ROOT)