from rest_framework import serializers
from django.contrib.auth.models import User
from students.models import Student
from modules.models import Module, Course
from registrations.models import Registration
from accounts.models import OTPVerification, ContactMessage
from portalcontent.models import SiteConfiguration, NewsUpdate


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class StudentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Student
        fields = ['id', 'user', 'student_id', 'phone_number', 'date_of_birth', 
                 'address', 'profile_picture', 'full_name', 'created_at']
        read_only_fields = ['id', 'created_at', 'full_name']
    
    def get_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip()


class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = ['id', 'code', 'name', 'description', 'credits', 'category', 
                 'prerequisites', 'is_active']
        read_only_fields = ['id']


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'code', 'name', 'description', 'level', 'is_active']
        read_only_fields = ['id']


class RegistrationSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    module = ModuleSerializer(read_only=True)
    student_id = serializers.IntegerField(write_only=True)
    module_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Registration
        fields = ['id', 'student', 'module', 'student_id', 'module_id', 
                 'status', 'registration_date', 'grade', 'notes']
        read_only_fields = ['id', 'registration_date']
    
    def create(self, validated_data):
        student_id = validated_data.pop('student_id')
        module_id = validated_data.pop('module_id')
        
        try:
            student = Student.objects.get(id=student_id)
            module = Module.objects.get(id=module_id)
        except (Student.DoesNotExist, Module.DoesNotExist):
            raise serializers.ValidationError("Invalid student or module ID")
        
        # Check if already registered
        if Registration.objects.filter(student=student, module=module).exists():
            raise serializers.ValidationError("Already registered for this module")
            
        validated_data['student'] = student
        validated_data['module'] = module
        
        return super().create(validated_data)


class OTPVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = OTPVerification
        fields = ['id', 'user', 'otp_code', 'is_used', 'created_at', 'expires_at']
        read_only_fields = ['id', 'created_at', 'expires_at']


class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = ['id', 'name', 'email', 'subject', 'message', 'is_read', 'created_at']
        read_only_fields = ['id', 'created_at', 'is_read']


class SiteConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteConfiguration
        fields = ['id', 'site_name', 'site_description', 'contact_email', 
                 'contact_phone', 'academic_year', 
                 'is_registration_open', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class NewsUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsUpdate
        fields = ['id', 'title', 'content', 'is_published', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password', 'password_confirm']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile info (no password required)"""
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        read_only_fields = ['username']  # Don't allow username changes


class StudentProfileSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer()
    profile_picture = serializers.ImageField(required=False, allow_null=True)
    
    class Meta:
        model = Student
        fields = ['user', 'student_id', 'phone_number', 'date_of_birth', 'address', 'profile_picture']
    
    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = UserRegistrationSerializer().create(user_data)
        student = Student.objects.create(user=user, **validated_data)
        return student
    
    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)
        if user_data:
            user_serializer = UserProfileSerializer(instance.user, data=user_data, partial=True)
            if user_serializer.is_valid():
                user_serializer.save()
        
        # Update student fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
