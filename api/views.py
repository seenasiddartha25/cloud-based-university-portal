from rest_framework import viewsets, status, views
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.shortcuts import get_object_or_404
from django.db.models import Q
import random
from django.utils import timezone

from students.models import Student
from modules.models import Module, Course
from registrations.models import Registration
from accounts.models import OTPVerification, ContactMessage
from portalcontent.models import SiteConfiguration, NewsUpdate

from .serializers import (
    UserSerializer, StudentSerializer, ModuleSerializer, CourseSerializer,
    RegistrationSerializer, OTPVerificationSerializer, 
    ContactMessageSerializer, SiteConfigurationSerializer, 
    NewsUpdateSerializer, UserRegistrationSerializer, StudentProfileSerializer
)
class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Students can only see their own profile, staff can see all
        if self.request.user.is_staff:
            return Student.objects.all()
        try:
            student = Student.objects.get(user=self.request.user)
            return Student.objects.filter(id=student.id)
        except Student.DoesNotExist:
            return Student.objects.none()
    
    @action(detail=False, methods=['get'])
    def profile(self, request):
        """Get current user's student profile"""
        try:
            student = Student.objects.get(user=request.user)
            serializer = self.get_serializer(student)
            return Response(serializer.data)
        except Student.DoesNotExist:
            return Response(
                {'error': 'Student profile not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )


class ModuleViewSet(viewsets.ModelViewSet):
    queryset = Module.objects.filter(is_active=True)
    serializer_class = ModuleSerializer
    
    def get_permissions(self):
        # Public can view modules, only staff can create, update, delete
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
            # You might want to add custom staff permission here
        return [permission() for permission in permission_classes]


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.filter(is_active=True)
    serializer_class = CourseSerializer
    
    def get_permissions(self):
        # Public can view courses, only staff can create, update, delete
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
            # You might want to add custom staff permission here
        return [permission() for permission in permission_classes]


class RegistrationViewSet(viewsets.ModelViewSet):
    queryset = Registration.objects.all()
    serializer_class = RegistrationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Students can only see their own registrations
        if self.request.user.is_staff:
            return Registration.objects.all()
        try:
            student = Student.objects.get(user=self.request.user)
            return Registration.objects.filter(student=student)
        except Student.DoesNotExist:
            return Registration.objects.none()
    
    def create(self, request, *args, **kwargs):
        # Automatically set student to current user's student profile
        try:
            student = Student.objects.get(user=request.user)
            # Create a mutable copy of the data
            data = request.data.copy()
            data['student_id'] = student.id
            
            # Create serializer with modified data
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except Student.DoesNotExist:
            return Response(
                {'error': 'Student profile required to register for modules'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def my_registrations(self, request):
        """Get current user's registrations"""
        try:
            student = Student.objects.get(user=request.user)
            registrations = Registration.objects.filter(student=student)
            
            # Filter by status if provided
            status_filter = request.query_params.get('status')
            if status_filter:
                registrations = registrations.filter(status=status_filter)
            
            serializer = self.get_serializer(registrations, many=True)
            return Response(serializer.data)
        except Student.DoesNotExist:
            return Response(
                {'error': 'Student profile not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )


class ContactMessageViewSet(viewsets.ModelViewSet):
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer
    
    def get_permissions(self):
        # Anyone can create contact messages, only staff can view all
        if self.action == 'create':
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]


class NewsUpdateViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = NewsUpdate.objects.filter(is_published=True).order_by('-created_at')
    serializer_class = NewsUpdateSerializer
    permission_classes = [AllowAny]


class SiteConfigurationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SiteConfiguration.objects.all()
    serializer_class = SiteConfigurationSerializer
    permission_classes = [AllowAny]


@api_view(['POST'])
@permission_classes([AllowAny])
def register_student(request):
    """Register a new student user"""
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        # Create user but don't activate yet
        user = User.objects.create_user(
            username=serializer.validated_data['username'],
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password'],
            first_name=serializer.validated_data.get('first_name', ''),
            last_name=serializer.validated_data.get('last_name', ''),
            is_active=False  # User is inactive until OTP verified
        )
        
        # Generate and send OTP
        otp = ''.join(str(random.randint(0, 9)) for _ in range(6))
        verification = OTPVerification.objects.create(
            user=user,
            otp=otp,
            purpose='registration',
            expires_at=timezone.now() + timezone.timedelta(minutes=10)
        )
        
        # In a real app, you'd send email here with OTP
        # For testing, we'll return it in response
        return Response({
            'success': True, 
            'message': 'Registration successful! Please verify your email with OTP.',
            'user_id': user.id,
            'otp': otp  # In production, remove this and send via email
        })
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_register_otp(request):
    """Verify OTP for user registration"""
    user_id = request.data.get('user_id')
    otp = request.data.get('otp')
    
    if not user_id or not otp:
        return Response(
            {'error': 'User ID and OTP are required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        user = User.objects.get(id=user_id, is_active=False)
        verification = OTPVerification.objects.filter(
            user=user, 
            otp=otp, 
            purpose='registration',
            is_used=False,
            expires_at__gt=timezone.now()
        ).first()
        
        if verification:
            # Activate user
            user.is_active = True
            user.save()
            
            # Mark OTP as used
            verification.is_used = True
            verification.save()
            
            # Auto-login the user
            login(request, user)
            
            return Response({
                'success': True,
                'message': 'Account verified successfully! You are now logged in.'
            })
        else:
            return Response(
                {'error': 'Invalid or expired OTP'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    except User.DoesNotExist:
        return Response(
            {'error': 'User not found or already activated'}, 
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def user_login(request):
    """Login a user and return token"""
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response(
            {'error': 'Username and password are required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = authenticate(username=username, password=password)
    
    if user:
        if user.is_active:
            login(request, user)
            return Response({
                'success': True,
                'message': 'Login successful',
                'user': UserSerializer(user).data
            })
        else:
            return Response(
                {'error': 'Account not activated. Please verify your email.'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
    else:
        return Response(
            {'error': 'Invalid username or password'}, 
            status=status.HTTP_401_UNAUTHORIZED
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_request(request):
    """Request password reset OTP"""
    email = request.data.get('email')
    
    if not email:
        return Response(
            {'error': 'Email is required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        user = User.objects.get(email=email)
        
        # Generate and send OTP
        otp = ''.join(str(random.randint(0, 9)) for _ in range(6))
        verification = OTPVerification.objects.create(
            user=user,
            otp=otp,
            purpose='password_reset',
            expires_at=timezone.now() + timezone.timedelta(minutes=10)
        )
        
        # In a real app, you'd send email here with OTP
        return Response({
            'success': True,
            'message': 'Password reset OTP sent to your email',
            'user_id': user.id,
            'otp': otp  # In production, remove this and send via email
        })
    except User.DoesNotExist:
        # For security, don't reveal if email exists or not
        return Response({
            'success': True,
            'message': 'If your email is registered, you will receive a password reset code'
        })


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_password_reset_otp(request):
    """Verify OTP for password reset"""
    user_id = request.data.get('user_id')
    otp = request.data.get('otp')
    
    if not user_id or not otp:
        return Response(
            {'error': 'User ID and OTP are required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        user = User.objects.get(id=user_id)
        verification = OTPVerification.objects.filter(
            user=user, 
            otp=otp, 
            purpose='password_reset',
            is_used=False,
            expires_at__gt=timezone.now()
        ).first()
        
        if verification:
            # Mark OTP as used
            verification.is_used = True
            verification.save()
            
            return Response({
                'success': True,
                'message': 'OTP verified successfully. You can now set a new password.',
                'user_id': user.id,
                'otp_verified': True
            })
        else:
            return Response(
                {'error': 'Invalid or expired OTP'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    except User.DoesNotExist:
        return Response(
            {'error': 'User not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def set_new_password(request):
    """Set new password after OTP verification"""
    user_id = request.data.get('user_id')
    password = request.data.get('password')
    
    if not user_id or not password:
        return Response(
            {'error': 'User ID and password are required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if len(password) < 8:
        return Response(
            {'error': 'Password must be at least 8 characters'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        user = User.objects.get(id=user_id)
        
        # Check if user has a verified OTP for password reset
        verification = OTPVerification.objects.filter(
            user=user,
            purpose='password_reset',
            is_used=True,
            expires_at__gt=timezone.now() - timezone.timedelta(minutes=30)  # Allow 30 mins after OTP verification
        ).exists()
        
        if verification:
            user.set_password(password)
            user.save()
            
            return Response({
                'success': True,
                'message': 'Password changed successfully. You can now login with your new password.'
            })
        else:
            return Response(
                {'error': 'OTP verification required before setting new password'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    except User.DoesNotExist:
        return Response(
            {'error': 'User not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    """Get dashboard statistics for current user"""
    try:
        student = Student.objects.get(user=request.user)
        registrations = Registration.objects.filter(student=student)
        
        # Calculate total credits from registered modules  
        total_credits = 0
        for reg in registrations.filter(status__in=['enrolled', 'completed']).select_related('module'):
            total_credits += reg.module.credits
        
        stats = {
            'total_registrations': registrations.count(),
            'active_registrations': registrations.filter(status='enrolled').count(),
            'completed_modules': registrations.filter(status='completed').count(),
            'pending_registrations': registrations.filter(status='pending').count(),
            'total_credits': total_credits,
        }
        
        return Response(stats)
    except Student.DoesNotExist:
        return Response(
            {'error': 'Student profile not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET', 'PUT', 'POST'])
@permission_classes([IsAuthenticated])
def profile_view(request):
    """
    Handle profile CRUD operations
    """
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        # Create student profile if it doesn't exist
        if request.method == 'POST':
            student = Student.objects.create(user=request.user)
        else:
            return Response(
                {'error': 'Student profile not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    if request.method == 'GET':
        # Return user and student data
        user_data = UserSerializer(request.user).data
        student_data = StudentSerializer(student).data
        return Response({
            'username': user_data['username'],
            'first_name': user_data['first_name'],
            'last_name': user_data['last_name'],
            'email': user_data['email'],
            'student': student_data
        })
    
    elif request.method in ['PUT', 'POST']:
        # Update user and student data
        user_data = {
            'first_name': request.data.get('first_name', request.user.first_name),
            'last_name': request.data.get('last_name', request.user.last_name),
            'email': request.data.get('email', request.user.email),
        }
        
        # Update user
        user_serializer = UserSerializer(request.user, data=user_data, partial=True)
        if user_serializer.is_valid():
            user_serializer.save()
        
        # Update student
        student_data = {
            'phone_number': request.data.get('phone_number', student.phone_number),
            'address': request.data.get('address', student.address),
            'date_of_birth': request.data.get('date_of_birth', student.date_of_birth),
        }
        
        if 'profile_picture' in request.FILES:
            student_data['profile_picture'] = request.FILES['profile_picture']
        
        student_serializer = StudentSerializer(student, data=student_data, partial=True)
        if student_serializer.is_valid():
            student_serializer.save()
            
            # Return updated data
            updated_user_data = UserSerializer(request.user).data
            updated_student_data = StudentSerializer(student).data
            return Response({
                'username': updated_user_data['username'],
                'first_name': updated_user_data['first_name'],
                'last_name': updated_user_data['last_name'],
                'email': updated_user_data['email'],
                'student': updated_student_data
            })
        else:
            return Response(student_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_view(request):
    """
    Get dashboard data for authenticated user
    """
    try:
        student = Student.objects.get(user=request.user)
        
        # Get student's registrations
        registrations = Registration.objects.filter(student=student)
        modules_count = registrations.count()
        
        user_data = UserSerializer(request.user).data
        student_data = StudentSerializer(student).data
        
        return Response({
            'profile': {
                'user': user_data,
                'student': student_data
            },
            'modules': RegistrationSerializer(registrations, many=True).data,
            'stats': {
                'modules_count': modules_count,
                'total_registrations': registrations.count()
            }
        })
    except Student.DoesNotExist:
        return Response(
            {'error': 'Student profile not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_modules_view(request):
    """
    Get modules registered by the current user
    """
    try:
        student = Student.objects.get(user=request.user)
        registrations = Registration.objects.filter(student=student)
        
        # Return registrations as a list
        return Response(RegistrationSerializer(registrations, many=True).data)
    except Student.DoesNotExist:
        return Response(
            {'error': 'Student profile not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def submit_contact_form(request):
    """Submit contact form"""
    serializer = ContactMessageSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({'success': True, 'message': 'Your message has been sent successfully!'})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_site_stats(request):
    """Get site statistics"""
    stats = {
        'students': Student.objects.count(),
        'courses': Course.objects.count(),
        'modules': Module.objects.count(),
        'registrations': Registration.objects.count(),
        'satisfaction': '98%'  # Placeholder statistic
    }
    return Response(stats)


class StudentProfileView(views.APIView):
    """View for student profile CRUD operations"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get student profile for current user"""
        try:
            student = Student.objects.get(user=request.user)
            serializer = StudentProfileSerializer(student)
            return Response(serializer.data)
        except Student.DoesNotExist:
            return Response(
                {'error': 'Student profile not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    def put(self, request):
        """Update student profile for current user"""
        try:
            student = Student.objects.get(user=request.user)
            data = request.data.copy()
            if request.FILES:
                data['profile_picture'] = request.FILES.get('profile_picture')
            serializer = StudentProfileSerializer(student, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Student.DoesNotExist:
            return Response(
                {'error': 'Student profile not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    def patch(self, request):
        """Partially update student profile for current user (supports file upload)"""
        try:
            student = Student.objects.get(user=request.user)
            data = request.data.copy()
            if request.FILES:
                data['profile_picture'] = request.FILES.get('profile_picture')
            serializer = StudentProfileSerializer(student, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Student.DoesNotExist:
            return Response(
                {'error': 'Student profile not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )


class DashboardView(views.APIView):
    """View for student dashboard data"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get dashboard data for current user"""
        try:
            student = Student.objects.get(user=request.user)
            
            # Get student registrations
            registrations = Registration.objects.filter(student=student).select_related('module')
            reg_serializer = RegistrationSerializer(registrations, many=True)
            
            # Get stats - calculate total credits from courses
            total_credits = 0
            for reg in registrations:
                if reg.status in ['enrolled', 'completed']:
                    total_credits += reg.module.credits
            
            pending_registrations = registrations.filter(status='pending').count()
            completed_modules = registrations.filter(status='completed').count()
            
            data = {
                'student': StudentSerializer(student).data,
                'registrations': reg_serializer.data,
                'stats': {
                    'total_credits': total_credits,
                    'pending_registrations': pending_registrations,
                    'completed_modules': completed_modules,
                    'total_registrations': registrations.count(),
                }
            }
            return Response(data)
        except Student.DoesNotExist:
            return Response(
                {'error': 'Student profile not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )


class MyModulesView(views.APIView):
    """View for student's registered modules"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get modules registered by current user"""
        try:
            student = Student.objects.get(user=request.user)
            registrations = Registration.objects.filter(student=student).select_related('module')
            
            # Extract modules from registrations
            modules = [reg.module for reg in registrations]
            serializer = ModuleSerializer(modules, many=True)
            
            return Response({
                'modules': serializer.data,
                'count': len(modules)
            })
        except Student.DoesNotExist:
            return Response(
                {'error': 'Student profile not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )


@api_view(['POST'])
@permission_classes([IsAuthenticated])  
def register_for_module(request, module_id):
    """Register current user for a module"""
    try:
        module = Module.objects.get(id=module_id, is_active=True)
    except Module.DoesNotExist:
        return Response({
            'success': False, 
            'message': 'Module not found or not available'
        }, status=404)
    
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        return Response({
            'success': False, 
            'message': 'Student profile not found'
        }, status=404)
    
    # Check if already registered
    if Registration.objects.filter(student=student, module=module).exists():
        return Response({
            'success': False, 
            'message': 'You are already registered for this module'
        }, status=400)
    
    # Create registration
    Registration.objects.create(
        student=student,
        module=module,
        status='enrolled'
    )
    
    return Response({'success': True, 'message': 'Successfully registered for module'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def unregister_from_module(request, module_id):
    """Unregister current user from a module"""
    try:
        module = Module.objects.get(id=module_id)
    except Module.DoesNotExist:
        return Response({
            'success': False, 
            'message': 'Module not found'
        }, status=404)
    
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        return Response({
            'success': False, 
            'message': 'Student profile not found'
        }, status=404)
    
    try:
        registration = Registration.objects.get(student=student, module=module)
        registration.delete()
        return Response({'success': True, 'message': 'Successfully unregistered from module'})
    except Registration.DoesNotExist:
        return Response({
            'success': False, 
            'message': 'You are not registered for this module'
        }, status=400)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_profile_photo(request):
    """Upload profile photo for current user"""
    try:
        student = Student.objects.get(user=request.user)
        if 'profile_picture' not in request.FILES:
            return Response(
                {'error': 'No file provided'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        student.profile_picture = request.FILES['profile_picture']
        student.save()
        
        serializer = StudentProfileSerializer(student)
        return Response(serializer.data)
    except Student.DoesNotExist:
        return Response(
            {'error': 'Student profile not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
