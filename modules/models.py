from django.db import models
from django.utils.text import slugify


class Course(models.Model):
    name = models.CharField(max_length=200)  # This is the title
    code = models.SlugField(max_length=20, unique=True)
    description = models.TextField(default="Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.")
    image_url = models.URLField(max_length=500, blank=True, null=True, help_text="URL for course image (e.g., from Unsplash)")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    def get_image_url(self):
        """Get image URL with fallback to default"""
        if self.image_url:
            return self.image_url
        # Default course image
        return 'https://images.unsplash.com/photo-1523050854058-8df90110c9f1?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80'
    
    def get_total_credits(self):
        """Get total credits for all modules in this course"""
        return self.modules.aggregate(models.Sum('credits'))['credits__sum'] or 0
    
    def get_module_count(self):
        """Get number of modules in this course"""
        return self.modules.count()
    
    def save(self, *args, **kwargs):
        if not self.code:
            self.code = slugify(self.name.replace(' ', '_'))[:20]
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'courses'
        verbose_name = 'Course'
        verbose_name_plural = 'Courses'
        ordering = ['code']


class Module(models.Model):
    CATEGORY_CHOICES = [
        ('CORE', 'Core'),
        ('ELECTIVE', 'Elective'), 
        ('OPTIONAL', 'Optional'),
        ('SPECIALIZED', 'Specialized'),
    ]
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    name = models.CharField(max_length=200)
    code = models.SlugField(max_length=20, unique=True)
    description = models.TextField(default="Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.")
    image_url = models.URLField(max_length=500, blank=True, null=True, help_text="URL for module image (e.g., from Unsplash)")
    credits = models.PositiveIntegerField(default=3)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='CORE')
    prerequisites = models.ManyToManyField('self', blank=True, symmetrical=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    def get_image_url(self):
        """Get image URL with fallback to default"""
        if self.image_url:
            return self.image_url
        # Default images based on category
        default_images = {
            'CORE': 'https://images.unsplash.com/photo-1481627834876-b7833e8f5570?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80',
            'ELECTIVE': 'https://images.unsplash.com/photo-1434030216411-0b793f4b4173?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80',
            'OPTIONAL': 'https://images.unsplash.com/photo-1460925895917-afdab827c52f?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80',
            'SPECIALIZED': 'https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80',
        }
        return default_images.get(self.category, default_images['CORE'])
    
    def save(self, *args, **kwargs):
        if not self.code:
            self.code = slugify(self.name.replace(' ', '_'))[:20]
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'modules'
        verbose_name = 'Module'
        verbose_name_plural = 'Modules'
        ordering = ['code']
