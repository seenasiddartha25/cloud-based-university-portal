from django.urls import path
from . import views

app_name = 'modules'

urlpatterns = [
    # Course URLs (main functionality)
    path('', views.course_list_view, name='course_list'),
    path('search/', views.course_search_view, name='course_search'),
    
    # Module URLs (legacy/admin) - put these before course detail to avoid conflicts
    path('modules/', views.module_list_view, name='module_list'),
    path('modules/<slug:code>/', views.module_detail_view, name='module_detail'),
    path('modules/search/', views.module_search_view, name='module_search'),
    
    # Course detail URLs - put these last to avoid conflicts
    path('<slug:code>/modules/', views.course_modules_view, name='course_modules'),
    path('<slug:code>/', views.course_detail_view, name='course_detail'),
]
