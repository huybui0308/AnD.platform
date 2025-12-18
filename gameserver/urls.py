"""
URL configuration for gameserver
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('gameserver.api.urls')),
    path('internal/', include('gameserver.api.urls')),
]
