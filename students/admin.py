from django.contrib import admin
from .models import Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['student_id', 'get_full_name', 'user_email', 'created_at']
    list_filter = ['created_at']
    search_fields = ['student_id', 'user__first_name', 'user__last_name', 'user__email']
    readonly_fields = ['student_id', 'created_at']
    
    def get_full_name(self, obj):
        return obj.user.get_full_name()
    get_full_name.short_description = 'Full Name'
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Email'
