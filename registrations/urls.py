from django.urls import path
from . import views

app_name = 'registrations'

urlpatterns = [
    path('my-registrations/', views.my_registrations_view, name='my_registrations'),
    path('<int:registration_id>/', views.registration_detail_view, name='registration_detail'),
    path('stats/', views.registration_stats_view, name='registration_stats'),
    
    # Admin URLs
    path('admin/', views.admin_registrations_view, name='admin_registrations'),
    path('admin/update/<int:registration_id>/', views.update_registration_status_view, name='update_registration_status'),
    path('admin/reports/', views.registration_reports_view, name='registration_reports'),
]
