from django.db import models


class SiteConfiguration(models.Model):
    site_name = models.CharField(max_length=100, default="University Module Registration")
    site_description = models.TextField(default="A comprehensive module registration system for university students")
    contact_email = models.EmailField(default="info@university.edu")
    contact_phone = models.CharField(max_length=20, default="+1-234-567-8900")
    address = models.TextField(default="123 University Ave, City, State 12345")
    about_content = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    is_registration_open = models.BooleanField(default=True, help_text="Is module registration currently open?")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.site_name
    
    def save(self, *args, **kwargs):
        # Ensure only one configuration exists
        if not self.pk and SiteConfiguration.objects.exists():
            raise ValueError("Only one site configuration is allowed")
        super().save(*args, **kwargs)
    
    @classmethod
    def get_site_config(cls):
        """Get or create the site configuration"""
        if cls.objects.exists():
            return cls.objects.first()
        
        config = cls.objects.create(
            site_name='University Module Registration',
            site_description='A comprehensive module registration system for university students',
            contact_email='info@university.edu',
            contact_phone='+1-234-567-8900',
            address='123 University Ave, City, State 12345',
        )
        return config
    
    class Meta:
        db_table = 'site_configuration'
        verbose_name = 'Site Configuration'
        verbose_name_plural = 'Site Configurations'


class PublishedNewsManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_published=True)


class NewsUpdate(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True)
    content = models.TextField()
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = models.Manager()
    published = PublishedNewsManager()
    
    def save(self, *args, **kwargs):
        # Generate slug if it doesn't exist
        if not self.slug:
            from django.utils.text import slugify
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            # Check for uniqueness
            while NewsUpdate.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title
    
    class Meta:
        db_table = 'news_updates'
        verbose_name = 'News Update'
        verbose_name_plural = 'News Updates'
        ordering = ['-created_at']
