from django.urls import path
from . import views

app_name = 'portalcontent'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('home/', views.home_view, name='home_alt'),
    path('about/', views.about_view, name='about'),
    path('contact/', views.contact_view, name='contact'),
    path('unauthorized/', views.unauthorized_view, name='unauthorized'),
]
