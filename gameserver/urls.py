"""
URL configuration for gameserver
"""
from django.contrib import admin
from django.urls import path, include

# Import patterns separately
from gameserver.api.urls import internal_patterns, public_patterns

urlpatterns = [
    path('admin/', admin.site.urls),
    path('internal/', include(internal_patterns)),
    path('api/', include(public_patterns)),
]
