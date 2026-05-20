from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'api'

# Create router for ViewSets
router = DefaultRouter()
router.register(r'modules', views.ModuleViewSet)
router.register(r'courses', views.CourseViewSet)
router.register(r'students', views.StudentViewSet)
router.register(r'registrations', views.RegistrationViewSet)
router.register(r'contact-messages', views.ContactMessageViewSet)
router.register(r'news', views.NewsUpdateViewSet)
router.register(r'site-config', views.SiteConfigurationViewSet)

urlpatterns = [
    # API router URLs
    path('', include(router.urls)),
    
    # Authentication APIs
    path('register/', views.register_student, name='register'),
    path('verify-register-otp/', views.verify_register_otp, name='verify_register_otp'),
    path('login/', views.user_login, name='login'),
    path('password-reset-request/', views.password_reset_request, name='password_reset_request'),
    path('verify-password-reset-otp/', views.verify_password_reset_otp, name='verify_password_reset_otp'),
    path('set-new-password/', views.set_new_password, name='set_new_password'),
    
    # Student APIs
    path('profile/', views.StudentProfileView.as_view(), name='profile'),
    path('profile/photo/', views.upload_profile_photo, name='upload_profile_photo'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('my-modules/', views.MyModulesView.as_view(), name='my_modules'),
    
    # Module registration APIs
    path('modules/<int:module_id>/register/', views.register_for_module, name='register_for_module'),
    path('modules/<int:module_id>/unregister/', views.unregister_from_module, name='unregister_from_module'),
    
    # Site APIs
    path('contact/', views.submit_contact_form, name='contact_form'),
    path('stats/', views.get_site_stats, name='site_stats'),
    
    # DRF Auth URLs (for browsable API)
    path('auth/', include('rest_framework.urls')),
]
