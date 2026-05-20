from django.contrib import admin
from .models import Course, Module

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'is_active']
    list_filter = ['is_active']
    search_fields = ['code', 'name', 'description']
    ordering = ['code']
    list_editable = ['is_active']
    
    fieldsets = (
        ('Course Information', {
            'fields': ('code', 'name', 'description')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'course', 'credits', 'category', 'is_active']
    list_filter = ['course', 'category', 'is_active', 'credits']
    search_fields = ['code', 'name', 'description', 'course__name', 'course__code']
    ordering = ['course__code', 'code']
    list_editable = ['is_active']
    
    fieldsets = (
        ('Module Information', {
            'fields': ('course', 'code', 'name', 'description', 'image_url')
        }),
        ('Academic Details', {
            'fields': ('credits', 'category', 'prerequisites')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )
