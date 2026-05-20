from django.db import models
from django.contrib.auth.models import User
from students.models import Student
from modules.models import Module


class Registration(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('enrolled', 'Enrolled'),
        ('completed', 'Completed'),
        ('dropped', 'Dropped'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='registrations')
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='registrations')
    registration_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    grade = models.CharField(max_length=2, blank=True, help_text="Final grade (A, B, C, D, F)")
    notes = models.TextField(blank=True)
    
    def __str__(self):
        full_name = self.student.user.get_full_name()
        if not full_name.strip():
            full_name = self.student.user.username
        return f"{full_name} - {self.module.code}"
    
    class Meta:
        db_table = 'registrations'
        verbose_name = 'Registration'
        verbose_name_plural = 'Registrations'
        unique_together = ['student', 'module']
        ordering = ['-registration_date']
