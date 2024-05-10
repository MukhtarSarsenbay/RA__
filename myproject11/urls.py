# myproject/urls.py
from django.contrib import admin
from django.urls import path, include
from myapp.views import input_values

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('myapp.urls')),  # Include your app's URLs heresss
    path('input_values/', include('myapp.urls')),
]
