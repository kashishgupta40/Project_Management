from django.urls import path

from .views import custom_logout_view

from . import views


app_name = 'account'


urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('logout/', custom_logout_view, name='logout'),
]