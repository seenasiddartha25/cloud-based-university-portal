from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.utils import timezone

from .models import Registration
from students.models import Student
from modules.models import Module, Course


def is_staff_member(user):
    """Check if user is staff member"""
    return user.is_staff


@login_required
def my_registrations_view(request):
    """View current user's registrations"""
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        messages.error(request, 'Please complete your student profile first.')
        return redirect('students:profile_setup')
    
    registrations = Registration.objects.filter(student=student).select_related('module').order_by('-registration_date')
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        registrations = registrations.filter(status=status_filter)
    
    # Pagination
    paginator = Paginator(registrations, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'student': student,
        'status_filter': status_filter,
        'status_choices': Registration.STATUS_CHOICES,
    }
    return render(request, 'registrations/my_registrations.html', context)


@login_required
def registration_detail_view(request, registration_id):
    """View detailed registration information"""
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        messages.error(request, 'Student profile not found.')
        return redirect('students:profile_setup')
    
    registration = get_object_or_404(Registration, id=registration_id, student=student)
    
    context = {
        'registration': registration,
        'student': student,
    }
    return render(request, 'registrations/registration_detail.html', context)


@login_required
@user_passes_test(is_staff_member)
def admin_registrations_view(request):
    """Admin view of all registrations"""
    registrations = Registration.objects.select_related('student__user', 'module').order_by('-registration_date')
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        registrations = registrations.filter(
            Q(student__user__username__icontains=search_query) |
            Q(student__user__email__icontains=search_query) |
            Q(student__student_id__icontains=search_query) |
            Q(module__code__icontains=search_query) |
            Q(module__name__icontains=search_query)
        )
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        registrations = registrations.filter(status=status_filter)
    
    # Filter by module
    module_filter = request.GET.get('module')
    if module_filter:
        registrations = registrations.filter(module_id=module_filter)
    
    # Pagination
    paginator = Paginator(registrations, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get filter options
    modules = Module.objects.filter(is_active=True).order_by('code')
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'module_filter': module_filter,
        'modules': modules,
        'status_choices': Registration.STATUS_CHOICES,
    }
    return render(request, 'registrations/admin_registrations.html', context)


@login_required
@user_passes_test(is_staff_member)
def update_registration_status_view(request, registration_id):
    """Update registration status (admin only)"""
    registration = get_object_or_404(Registration, id=registration_id)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        grade = request.POST.get('grade', '')
        notes = request.POST.get('notes', '')
        
        if new_status in dict(Registration.STATUS_CHOICES):
            registration.status = new_status
            registration.grade = grade
            registration.notes = notes
            registration.save()
            
            messages.success(request, f'Registration status updated for {registration.student.user.get_full_name()}')
        else:
            messages.error(request, 'Invalid status selected.')
    
    return redirect('registrations:admin_registrations')


@login_required
def registration_stats_view(request):
    """View registration statistics"""
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        messages.error(request, 'Student profile not found.')
        return redirect('students:profile_setup')
    
    registrations = Registration.objects.filter(student=student)
    
    stats = {
        'total_registrations': registrations.count(),
        'pending': registrations.filter(status='pending').count(),
        'enrolled': registrations.filter(status='enrolled').count(),
        'completed': registrations.filter(status='completed').count(),
        'dropped': registrations.filter(status='dropped').count(),
        'total_credits': sum(reg.module.credits for reg in registrations.filter(status__in=['enrolled', 'completed'])),
        'completed_credits': sum(reg.module.credits for reg in registrations.filter(status='completed')),
    }
    
    context = {
        'student': student,
        'stats': stats,
    }
    return render(request, 'registrations/registration_stats.html', context)


@login_required
@user_passes_test(is_staff_member)
def registration_reports_view(request):
    """Generate registration reports (admin only)"""
    # Overall statistics
    total_registrations = Registration.objects.count()
    active_students = Student.objects.filter(registration__isnull=False).distinct().count()
    
    # Status breakdown
    status_stats = {}
    for status_code, status_name in Registration.STATUS_CHOICES:
        status_stats[status_name] = Registration.objects.filter(status=status_code).count()
    
    # Module popularity
    popular_modules = Module.objects.annotate(
        registration_count=Count('registration')
    ).order_by('-registration_count')[:10]
    
    # Recent registrations
    recent_registrations = Registration.objects.select_related(
        'student__user', 'module'
    ).order_by('-registration_date')[:10]
    
    context = {
        'total_registrations': total_registrations,
        'active_students': active_students,
        'status_stats': status_stats,
        'popular_modules': popular_modules,
        'recent_registrations': recent_registrations,
    }
    return render(request, 'registrations/registration_reports.html', context)
