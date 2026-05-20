from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'students'

urlpatterns = [
    # Authentication URLs
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('register/', views.register_view, name='register'),
    path('password/reset/', auth_views.PasswordResetView.as_view(
        template_name='students/password_reset.html',
        email_template_name='emails/password_reset_email.html',
        success_url='/students/password/reset/done/'
    ), name='password_reset'),
    path('password/reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='students/password_reset_verify.html'
    ), name='password_reset_done'),
    path('password/reset/confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='students/password_reset_confirm.html',
        success_url='/students/password/reset/complete/'
    ), name='password_reset_confirm'),
    path('password/reset/complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='students/password_reset_verify.html'
    ), name='password_reset_complete'),
    
    # Student Dashboard and Profile
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('profile/setup/', views.profile_setup_view, name='profile_setup'),
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),
    
    # Course URLs (main functionality)
    path('courses/', views.courses_view, name='courses'),
    path('registrations/', views.registrations_view, name='registrations'),
    path('register/course/<slug:course_code>/', views.register_course_view, name='register_course'),
    path('unregister/course/<slug:course_code>/', views.unregister_course_view, name='unregister_course'),
    
    # Module URLs (legacy/backward compatibility)
    path('student/modules/', views.modules_view, name='modules'),
    path('register/<slug:module_code>/', views.register_module_view, name='register_module'),
    path('unregister/<slug:module_code>/', views.unregister_module_view, name='unregister_module'),
]
