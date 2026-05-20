from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from datetime import date


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    student_id = models.CharField(max_length=20, unique=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    phone_number = models.CharField(
        max_length=15, 
        blank=True, 
        validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Enter a valid phone number.")]
    )
    address = models.CharField(max_length=255, blank=True)
    profile_picture = models.ImageField(upload_to='student_profiles/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    @property
    def full_name(self):
        """Get full name of the student"""
        return self.user.get_full_name() or self.user.username
    
    @property
    def age(self):
        """Calculate age from date of birth"""
        if self.date_of_birth:
            today = date.today()
            return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        return None
    
    def __str__(self):
        return f"{self.full_name} ({self.student_id})"
    
    def save(self, *args, **kwargs):
        if not self.student_id:
            # Generate unique student ID
            last_student = Student.objects.filter(student_id__startswith='STU').order_by('student_id').last()
            if last_student:
                last_id = int(last_student.student_id[3:])
                new_id = last_id + 1
            else:
                new_id = 1
            self.student_id = f'STU{new_id:05d}'
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'students'
        verbose_name = 'Student'
        verbose_name_plural = 'Students'
