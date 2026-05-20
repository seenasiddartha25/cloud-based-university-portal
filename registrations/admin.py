from django.contrib import admin
from .models import Registration

@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ['student', 'module', 'status', 'registration_date', 'grade']
    list_filter = ['status', 'registration_date', 'module__course']
    search_fields = ['student__user__username', 'student__user__email', 'module__code', 'module__name']
    ordering = ['-registration_date']
    list_editable = ['status', 'grade']
    date_hierarchy = 'registration_date'
    
    fieldsets = (
        ('Registration Details', {
            'fields': ('student', 'module', 'status')
        }),
        ('Academic Information', {
            'fields': ('grade', 'notes')
        }),
        ('Timestamps', {
            'fields': ('registration_date',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['registration_date']
