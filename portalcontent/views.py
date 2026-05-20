from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from accounts.models import ContactMessage
from .models import SiteConfiguration, NewsUpdate
from modules.models import Course, Module
from students.models import Student
from registrations.models import Registration
import json
import os
import requests
from django.conf import settings
from datetime import datetime


def home_view(request):
    """Home page view"""
    site_config = SiteConfiguration.get_site_config()
    news_updates = NewsUpdate.published.all()[:3]

    # Add stats for the home page
    stats = {
        'total_students': Student.objects.count(),
        'total_courses': Course.objects.count(),
        'total_modules': Module.objects.count(),
        'total_registrations': Registration.objects.count(),
    }

    # Fetch external news via NewsAPI (optional, depends on NEWSAPI_KEY)
    newsapi_articles = []
    api_key = os.environ.get('NEWSAPI_KEY') or getattr(settings, 'NEWSAPI_KEY', '')
    if api_key:
        try:
            params = {
                'q': 'university OR education OR students',
                'language': 'en',
                'sortBy': 'publishedAt',
                'pageSize': 6,
                'apiKey': api_key,
            }
            resp = requests.get('https://newsapi.org/v2/everything', params=params, timeout=5)
            if resp.status_code == 200:
                payload = resp.json()
                articles = payload.get('articles', [])

                def parse_dt(s):
                    try:
                        return datetime.fromisoformat(s.replace('Z', '+00:00')) if s else None
                    except Exception:
                        return None

                newsapi_articles = [
                    {
                        'title': a.get('title'),
                        'description': a.get('description'),
                        'url': a.get('url'),
                        'urlToImage': a.get('urlToImage'),
                        'source': (a.get('source') or {}).get('name'),
                        'publishedAt': parse_dt(a.get('publishedAt')),
                    }
                    for a in articles if a.get('title') and a.get('url')
                ][:6]
        except Exception:
            # Silently ignore errors and keep the external news empty
            newsapi_articles = []

    context = {
        'site_config': site_config,
        'news_updates': news_updates,
        'stats': stats,
        'newsapi_articles': newsapi_articles,
    }
    return render(request, 'portalcontent/home.html', context)


def about_view(request):
    """About page view"""
    site_config = SiteConfiguration.get_site_config()
    
    context = {
        'site_config': site_config,
    }
    return render(request, 'portalcontent/about.html', context)


@csrf_protect
def contact_view(request):
    """Contact page view"""
    site_config = SiteConfiguration.get_site_config()
    
    if request.method == 'POST':
        # Handle form submission
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        phone = request.POST.get('phone', '')  # Phone is optional
        
        # Validation
        if not all([name, email, subject, message]):
            return JsonResponse({
                'success': False,
                'message': 'All fields are required.'
            })
        
        try:
            # Create contact message
            contact_message = ContactMessage.objects.create(
                name=name,
                email=email,
                subject=subject,
                message=message,
                phone=phone
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Thank you! Your message has been sent successfully.'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': 'Sorry, there was an error sending your message. Please try again.'
            })
    
    context = {
        'site_config': site_config,
    }
    return render(request, 'portalcontent/contact.html', context)


def unauthorized_view(request):
    """Unauthorized access page"""
    return render(request, 'portalcontent/unauthorized.html')
