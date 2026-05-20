from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import JsonResponse

from .models import Course, Module
from registrations.models import Registration
from students.models import Student


def course_list_view(request):
    """Public view of all active courses"""
    courses = Course.objects.filter(is_active=True)
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        courses = courses.filter(
            Q(name__icontains=search_query) |
            Q(code__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    # Pagination
    paginator = Paginator(courses, 6)  # Show 6 courses per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'courses': courses,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'search_query': search_query,
    }
    return render(request, 'modules/course_list.html', context)


def course_detail_view(request, code):
    """Detailed view of a course with its modules"""
    course = get_object_or_404(Course, code=code, is_active=True)
    modules = Module.objects.filter(course=course, is_active=True)
    
    context = {
        'course': course,
        'modules': modules,
    }
    return render(request, 'modules/course_detail.html', context)


def course_modules_view(request, code):
    """Show modules for a specific course (replaces course detail)"""
    course = get_object_or_404(Course, code=code, is_active=True)
    modules = Module.objects.filter(course=course, is_active=True).order_by('code')
    
    # Pagination
    paginator = Paginator(modules, 12)  # Show 12 modules per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Check user registration status for modules
    user_registered_modules = []
    user_registered_module_ids = []
    
    if request.user.is_authenticated:
        try:
            student = Student.objects.get(user=request.user)
            # Get user's registered modules
            registrations = Registration.objects.filter(student=student, module__course=course)
            user_registered_modules = [reg.module for reg in registrations]
            user_registered_module_ids = [reg.module.id for reg in registrations]
        except Student.DoesNotExist:
            pass
    
    context = {
        'course': course,
        'modules': modules,
        'page_obj': page_obj,
        'user_registered_modules': user_registered_modules,
        'user_registered_module_ids': user_registered_module_ids,
    }
    return render(request, 'modules/course_modules.html', context)


@login_required
def course_search_view(request):
    """AJAX search for courses"""
    query = request.GET.get('q', '')
    courses = Course.objects.filter(is_active=True)
    
    if query:
        courses = courses.filter(
            Q(name__icontains=query) |
            Q(code__icontains=query) |
            Q(description__icontains=query)
        )[:10]  # Limit to 10 results
    
    results = []
    for course in courses:
        results.append({
            'id': course.id,
            'code': course.code,
            'name': course.name,
        })
    
    return JsonResponse({'results': results})


# Keep the old module views for backward compatibility / admin purposes
def module_list_view(request):
    """Public view of all active modules"""
    modules = Module.objects.filter(is_active=True).select_related('course')
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        modules = modules.filter(
            Q(name__icontains=search_query) |
            Q(code__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Filter by credits
    credits = request.GET.get('credits')
    if credits:
        modules = modules.filter(credits=credits)

    # Pagination
    paginator = Paginator(modules, 12)  # Show 12 modules per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get filter options
    credit_options = Module.objects.filter(is_active=True).values_list('credits', flat=True).distinct()
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'credits': credits,
        'credit_options': sorted(set(credit_options)),
    }
    return render(request, 'modules/module_list.html', context)


def module_detail_view(request, code):
    """Detailed view of a module"""
    module = get_object_or_404(Module, code=code, is_active=True)
    
    context = {
        'module': module,
    }
    return render(request, 'modules/module_detail.html', context)


@login_required
def module_search_view(request):
    """AJAX search for modules"""
    query = request.GET.get('q', '')
    modules = Module.objects.filter(is_active=True)
    
    if query:
        modules = modules.filter(
            Q(name__icontains=query) |
            Q(code__icontains=query) |
            Q(description__icontains=query)
        )[:10]  # Limit to 10 results
    
    results = []
    for module in modules:
        results.append({
            'id': module.id,
            'code': module.code,
            'name': module.name,
            'credits': module.credits,
        })
    
    return JsonResponse({'results': results})