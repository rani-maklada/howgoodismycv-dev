from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.base, name='home'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='myapp/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('upload/', views.upload, name='upload'),
    path('home/', views.home, name='home'),
    path('contact/', views.contact, name='contact'),
    path('dashboard/id/<int:id>/', views.dashboard, name='dashboard'),
]
