from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect

from .models import Student
from modules.models import Course, Module
from registrations.models import Registration
from portalcontent.models import SiteConfiguration


def login_view(request):
    """Student login view"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', 'dashboard')
            messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'students/login.html')


def register_view(request):
    """Student registration view"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        
        # Basic validation
        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'students/register.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'students/register.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
            return render(request, 'students/register.html')
        
        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1,
            first_name=first_name,
            last_name=last_name
        )
        
        # Log the user in
        login(request, user)
        messages.success(request, 'Registration successful! Please complete your student profile.')
        return redirect('students:profile_setup')
    
    return render(request, 'students/register.html')


@login_required
def dashboard_view(request):
    """Student dashboard view"""
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        # If no student profile exists, redirect to create one
        messages.warning(request, 'Please complete your student profile.')
        return redirect('students:profile_setup')
    
    # Get student's registrations
    registrations = Registration.objects.filter(student=student).select_related('module')
    
    # Get available courses for registration
    site_config = SiteConfiguration.objects.first()
    available_courses = Course.objects.filter(is_active=True)
    
    # Calculate stats - now using module credits instead of course credits
    total_credits = sum(reg.module.credits for reg in registrations.filter(status__in=['enrolled', 'completed']))
    
    context = {
        'student': student,
        'registrations': registrations,
        'available_courses': available_courses[:5],  # Show only first 5
        'site_config': site_config,
        'stats': {
            'total_credits': total_credits,
            'total_registrations': registrations.count(),
        }
    }
    return render(request, 'students/dashboard.html', context)


@login_required
@csrf_protect
def profile_setup_view(request):
    """Student profile setup view"""
    try:
        student = Student.objects.get(user=request.user)
        # If profile exists, redirect to profile edit
        return redirect('students:profile_edit')
    except Student.DoesNotExist:
        pass
    
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        phone_number = request.POST.get('phone_number')
        date_of_birth = request.POST.get('date_of_birth')
        address = request.POST.get('address')
        profile_picture = request.FILES.get('profile_picture')
        
        # Validation
        if not all([student_id, phone_number, date_of_birth, address]):
            messages.error(request, 'All fields except profile picture are required.')
            return render(request, 'students/profile_setup.html')
        
        # Check if student ID is unique
        if Student.objects.filter(student_id=student_id).exists():
            messages.error(request, 'Student ID already exists.')
            return render(request, 'students/profile_setup.html')
        
        try:
            student = Student.objects.create(
                user=request.user,
                student_id=student_id,
                phone_number=phone_number,
                date_of_birth=date_of_birth,
                address=address,
                profile_picture=profile_picture
            )
            messages.success(request, 'Profile created successfully!')
            return redirect('students:dashboard')
        except Exception as e:
            messages.error(request, 'Failed to create profile. Please try again.')
    
    return render(request, 'students/profile_setup.html')


@login_required
@csrf_protect
def profile_edit_view(request):
    """Student profile edit view"""
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        return redirect('students:profile_setup')
    
    if request.method == 'POST':
        student.phone_number = request.POST.get('phone_number', student.phone_number)
        student.address = request.POST.get('address', student.address)
        
        if request.FILES.get('profile_picture'):
            student.profile_picture = request.FILES['profile_picture']
        
        try:
            student.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('students:dashboard')
        except Exception as e:
            messages.error(request, 'Failed to update profile. Please try again.')
    
    context = {'student': student}
    return render(request, 'students/profile_edit.html', context)


@login_required
def courses_view(request):
    """View available courses"""
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        return redirect('students:profile_setup')
    
    # Get all active courses
    courses = Course.objects.filter(is_active=True)
    
    # Get student's current module registrations
    student_module_registrations = Registration.objects.filter(student=student).values_list('module_id', flat=True)
    
    # Add registration status to courses based on module registrations
    for course in courses:
        # Check if student is registered for any modules in this course
        course_modules = course.modules.values_list('id', flat=True)
        course.has_module_registrations = any(module_id in student_module_registrations for module_id in course_modules)
        course.registered_module_count = len([m_id for m_id in course_modules if m_id in student_module_registrations])
        course.total_module_count = course.modules.count()
    
    context = {
        'student': student,
        'courses': courses,
    }
    return render(request, 'students/courses.html', context)


@login_required
def registrations_view(request):
    """View student's course registrations"""
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        return redirect('students:profile_setup')
    
    registrations = Registration.objects.filter(student=student).select_related('module').order_by('-registration_date')
    
    # Filter by status if specified
    status_filter = request.GET.get('status')
    if status_filter:
        registrations = registrations.filter(status=status_filter)
    
    context = {
        'student': student,
        'registrations': registrations,
        'status_filter': status_filter,
        'status_choices': Registration.STATUS_CHOICES
    }
    return render(request, 'students/registrations.html', context)


@login_required
@csrf_protect
def register_course_view(request, course_code):
    """Register for modules in a course - redirect to course modules page"""
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        messages.error(request, 'Please complete your student profile first.')
        return redirect('students:profile_setup')
    
    course = get_object_or_404(Course, code=course_code, is_active=True)
    
    # Redirect to course modules page for module-based registration
    messages.info(request, f'Please select specific modules to register for in {course.name}.')
    return redirect('modules:course_modules', code=course.code)


@login_required
@csrf_protect
def unregister_course_view(request, course_code):
    """Unregister from all modules in a course"""
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        messages.error(request, 'Student profile not found.')
        return redirect('students:profile_setup')
    
    course = get_object_or_404(Course, code=course_code)
    
    # Get all registrations for modules in this course
    course_modules = Module.objects.filter(course=course)
    registrations = Registration.objects.filter(
        student=student, 
        module__in=course_modules,
        status__in=['pending', 'enrolled']
    )
    
    if registrations.exists():
        count = registrations.count()
        registrations.delete()
        messages.success(request, f'Successfully unregistered from {count} module(s) in {course.name}.')
    else:
        messages.info(request, f'You are not registered for any modules in {course.name}.')
    
    return redirect('students:courses')


@login_required
@csrf_protect
def unregister_course_view(request, course_code):
    """Unregister from a course"""
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        messages.error(request, 'Student profile not found.')
        return redirect('students:profile_setup')
    
    course = get_object_or_404(Course, code=course_code)
    
    try:
        registration = Registration.objects.get(student=student, course=course)
        
        # Only allow unregistration for pending/enrolled status
        if registration.status in ['pending', 'enrolled']:
            registration.delete()
            messages.success(request, f'Successfully unregistered from {course.name}.')
        else:
            messages.error(request, f'Cannot unregister from {course.name}. Status: {registration.get_status_display()}')
    except Registration.DoesNotExist:
        messages.error(request, 'You are not registered for this course.')
    
    return redirect('students:registrations')


# Keep legacy module views for backward compatibility
@login_required
def modules_view(request):
    """View available modules (legacy)"""
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        return redirect('students:profile_setup')
    
    # Get all active modules
    modules = Module.objects.filter(is_active=True).select_related('course')
    
    context = {
        'student': student,
        'modules': modules,
    }
    return render(request, 'students/modules.html', context)


@login_required
@csrf_protect
@login_required
@csrf_protect  
def register_module_view(request, module_code):
    """Register for a module"""
    module = get_object_or_404(Module, code=module_code, is_active=True)
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        return redirect('students:profile_setup')
    
    # Check if already registered
    if Registration.objects.filter(student=student, module=module).exists():
        messages.warning(request, f'You are already registered for {module.name}')
    else:
        # Create registration
        Registration.objects.create(
            student=student,
            module=module,
            status='pending'
        )
        messages.success(request, f'Successfully registered for {module.name}')
    
    return redirect('modules:course_modules', code=module.course.code)


@login_required
@csrf_protect
def unregister_module_view(request, module_code):
    """Unregister from a module"""
    module = get_object_or_404(Module, code=module_code)
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        return redirect('students:profile_setup')
    
    # Check if registered
    try:
        registration = Registration.objects.get(student=student, module=module)
        registration.delete()
        messages.success(request, f'Successfully unregistered from {module.name}')
    except Registration.DoesNotExist:
        messages.warning(request, f'You are not registered for {module.name}')
    
    return redirect('modules:course_modules', code=module.course.code)
