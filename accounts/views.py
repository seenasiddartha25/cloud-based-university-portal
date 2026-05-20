from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.urls import reverse
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.utils import timezone
from django.http import JsonResponse
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
import random
import string

from .models import OTPVerification
from students.models import Student


def generate_otp():
    """Generate a 6-digit OTP"""
    return ''.join(random.choices(string.digits, k=6))


def send_otp_email(user, otp_code, otp_type='REGISTER'):
    """Send OTP email to user"""
    try:
        if otp_type == 'REGISTER':
            subject = 'Email Verification - University Module Registration System'
            html_template = 'emails/otp_verification.html'
            text_template = 'emails/otp_verification.txt'
        else:
            subject = 'Password Reset - University Module Registration System'
            html_template = 'emails/password_reset.html'
            text_template = 'emails/password_reset.txt'
        
        context = {
            'user': user,
            'otp_code': otp_code,
        }
        
        html_message = render_to_string(html_template, context)
        plain_message = render_to_string(text_template, context)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False


@csrf_protect
def register_view(request):
    """User registration view"""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        
        # Validation
        if not all([username, email, first_name, last_name, password, password_confirm]):
            messages.error(request, 'All fields are required.')
            return render(request, 'accounts/register.html')
        
        if password != password_confirm:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'accounts/register.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'accounts/register.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return render(request, 'accounts/register.html')
        
        # Create user
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=password
            )
            user.is_active = False  # User needs to verify email
            user.save()
            
            # Generate and send OTP
            otp_code = generate_otp()
            OTPVerification.objects.create(
                user=user,
                otp_code=otp_code,
                otp_type='REGISTER',
                expires_at=timezone.now() + timezone.timedelta(minutes=15)
            )
            
            # Send OTP email
            if send_otp_email(user, otp_code, 'REGISTER'):
                messages.success(request, 'Registration successful! Please check your email for the verification code.')
            else:
                messages.warning(request, f'Registration successful! Your verification code is: {otp_code} (Email sending failed)')
            
            return redirect('accounts:verify_otp', user_id=user.id)
            
        except Exception as e:
            messages.error(request, 'Registration failed. Please try again.')
            return render(request, 'accounts/register.html')
    
    return render(request, 'accounts/register.html')


@csrf_protect
def login_view(request):
    """User login view"""
    if request.user.is_authenticated:
        return redirect('students:dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if not username or not password:
            messages.error(request, 'Username and password are required.')
            return render(request, 'accounts/login.html')
        
        # Try to get user by username or email
        user = None
        if '@' in username:
            # Login with email
            try:
                user_obj = User.objects.get(email=username)
                user = authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                pass
        else:
            # Login with username
            user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if user.is_active:
                login(request, user)
                next_url = request.GET.get('next', 'students:dashboard')
                return redirect(next_url)
            else:
                # User exists but not verified
                messages.info(request, 'Your account is not verified. Please check your email for the verification code.')
                return redirect('accounts:verify_otp', user_id=user.id)
        else:
            # Check if user exists but not verified
            try:
                if '@' in username:
                    user_obj = User.objects.get(email=username)
                else:
                    user_obj = User.objects.get(username=username)
                
                if not user_obj.is_active:
                    # User exists but password might be wrong and not verified
                    messages.error(request, 'Account not verified. Please verify your email first.')
                    return redirect('accounts:verify_otp', user_id=user_obj.id)
                else:
                    messages.error(request, 'Invalid username or password.')
            except User.DoesNotExist:
                messages.error(request, 'Invalid username or password.')
    
    return render(request, 'accounts/login.html')


def logout_view(request):
    """User logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('portalcontent:home')


def verify_otp_view(request, user_id):
    """Verify OTP for email verification"""
    try:
        user = User.objects.get(id=user_id)
        otp_verification = OTPVerification.objects.filter(
            user=user, 
            is_used=False,
            expires_at__gt=timezone.now()
        ).first()
        
        if not otp_verification:
            messages.error(request, 'OTP expired or invalid.')
            return redirect('accounts:register')
        
        if request.method == 'POST':
            otp_code = request.POST.get('otp_code')
            
            if otp_code == otp_verification.otp_code:
                otp_verification.is_used = True
                otp_verification.save()
                
                user.is_active = True
                user.save()
                
                messages.success(request, 'Email verified successfully! You can now login.')
                return redirect('accounts:login')
            else:
                messages.error(request, 'Invalid OTP code.')
        
        context = {
            'user': user,
            'otp_verification': otp_verification
        }
        return render(request, 'accounts/verify_otp.html', context)
        
    except User.DoesNotExist:
        messages.error(request, 'Invalid user.')
        return redirect('accounts:register')


def resend_otp_view(request, user_id):
    """Resend OTP for email verification"""
    try:
        user = User.objects.get(id=user_id)
        
        # Invalidate old OTPs
        OTPVerification.objects.filter(user=user, is_used=False).delete()
        
        # Generate new OTP
        otp_code = generate_otp()
        OTPVerification.objects.create(
            user=user,
            otp_code=otp_code,
            otp_type='REGISTER',
            expires_at=timezone.now() + timezone.timedelta(minutes=15)
        )
        
        # Send OTP email
        if send_otp_email(user, otp_code, 'REGISTER'):
            messages.success(request, 'New verification code sent to your email.')
        else:
            messages.warning(request, f'New verification code: {otp_code} (Email sending failed)')
        
        return redirect('accounts:verify_otp', user_id=user.id)
        
    except User.DoesNotExist:
        messages.error(request, 'Invalid user.')
        return redirect('accounts:register')


@login_required
def profile_view(request):
    """User profile view"""
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        student = None
    
    context = {
        'student': student
    }
    return render(request, 'accounts/profile.html', context)


def admin_login_blocked(request):
    """Block admin login via /auth/login/ - redirect to unauthorized page"""
    messages.warning(request, 'Admin login via this URL is not allowed. Please use the admin panel directly.')
    return redirect('portalcontent:unauthorized')


class CustomPasswordResetView(auth_views.PasswordResetView):
    """Custom password reset view that sends HTML emails"""
    template_name = 'accounts/password_reset.html'
    email_template_name = 'emails/password_reset_email.html'
    html_email_template_name = 'emails/password_reset_email.html'  # Use same template for HTML
    success_url = reverse_lazy('accounts:password_reset_done')
    
    def send_mail(self, subject_template_name, email_template_name,
                  context, from_email, to_email, html_email_template_name=None):
        """Override to ensure HTML email is sent"""
        subject = render_to_string(subject_template_name or 'emails/password_reset_subject.txt', context)
        subject = ''.join(subject.splitlines())  # Remove newlines
        
        # Render HTML email
        html_email = render_to_string(html_email_template_name or email_template_name, context)
        
        # Create plain text version
        plain_email = strip_tags(html_email)
        
        send_mail(
            subject=subject,
            message=plain_email,
            from_email=from_email,
            recipient_list=[to_email],
            html_message=html_email,
        )


class CustomPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    """Custom password reset confirm view with better error handling"""
    template_name = 'accounts/password_reset_confirm.html'
    success_url = reverse_lazy('accounts:password_reset_complete')
    
    def form_valid(self, form):
        """Override to add success message"""
        response = super().form_valid(form)
        messages.success(self.request, 'Your password has been successfully changed!')
        return response
    
    def form_invalid(self, form):
        """Override to add error messages"""
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"{error}")
        return super().form_invalid(form)
