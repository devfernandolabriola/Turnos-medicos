from django.contrib import admin
from django.urls import path, include
from Turnosmedicos.views import index
from django.contrib.auth import views as auth_views
from Turnosmedicos.views import login_view, register_view, logout_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('Turnosmedicos.urls')),
    path('', index, name='index'),
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),
]


LOGIN_URL = '/login/' 
LOGIN_REDIRECT_URL = '/'


