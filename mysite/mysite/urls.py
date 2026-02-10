"""
URL configuration for mysite project.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("", include("blocks.urls")),  # Game at root
    path('admin/', admin.site.urls),
]
