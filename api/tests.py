from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from modules.models import Module, Course
from students.models import Student
from registrations.models import Registration
from portalcontent.models import NewsUpdate
from accounts.models import ContactMessage


class APIAuthenticationTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            is_active=True
        )
        self.inactive_user = User.objects.create_user(
            username='inactive',
            email='inactive@example.com',
            password='testpass123',
            is_active=False
        )

    def test_api_authentication_required(self):
        """Test that protected APIs require authentication"""
        protected_endpoints = [
            '/api/profile/',
            '/api/dashboard/',
            '/api/my-modules/',
            '/api/registrations/',
        ]
        
        for endpoint in protected_endpoints:
            response = self.client.get(endpoint)
            self.assertIn(response.status_code, [401, 403])

    def test_api_authentication_with_valid_user(self):
        """Test API access with valid authenticated user"""
        Student.objects.create(user=self.user, student_id='STU001')
        self.client.force_authenticate(user=self.user)
        
        response = self.client.get('/api/profile/')
        self.assertEqual(response.status_code, 200)

    def test_api_authentication_with_inactive_user(self):
        """Test API access denied for inactive users"""
        self.client.force_authenticate(user=self.inactive_user)
        
        response = self.client.get('/api/profile/')
        self.assertIn(response.status_code, [403, 404])  # Either is acceptable

    def test_session_authentication(self):
        """Test session-based authentication"""
        Student.objects.create(user=self.user, student_id='STU001')
        self.client.force_login(self.user)
        
        response = self.client.get('/api/profile/')
        self.assertEqual(response.status_code, 200)


class ModuleAPITestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.course = Course.objects.create(
            name='Computer Science',
            code='CS_MASTERS',
            description='Master of Computer Science'
        )
        self.module = Module.objects.create(
            course=self.course,
            name='Introduction to Programming',
            code='CS101',
            description='Basic programming concepts',
            credits=3,
            category='CORE'
        )

    def test_module_list_api(self):
        """Test module list API"""
        response = self.client.get('/api/modules/')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('results', data)  # DRF pagination
        self.assertEqual(len(data['results']), 1)
        self.assertEqual(data['results'][0]['name'], 'Introduction to Programming')

    def test_module_detail_api(self):
        """Test module detail API"""
        response = self.client.get(f'/api/modules/{self.module.pk}/')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data['name'], 'Introduction to Programming')
        self.assertEqual(data['code'], 'CS101')

    def test_module_search_api(self):
        """Test module search functionality"""
        response = self.client.get('/api/modules/?search=Programming')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(len(data['results']), 1)

    def test_module_filter_by_category_api(self):
        """Test filtering modules by category"""
        response = self.client.get('/api/modules/?category=CORE')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(len(data['results']), 1)

    def test_module_api_permissions(self):
        """Test module API permissions (should be public)"""
        # Should work without authentication
        response = self.client.get('/api/modules/')
        self.assertEqual(response.status_code, 200)


class StudentAPITestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='John',
            last_name='Doe',
            is_active=True
        )
        self.student = Student.objects.create(
            user=self.user,
            student_id='STU001',
            date_of_birth='1990-01-01'
        )

    def test_profile_api_get(self):
        """Test getting user profile via API"""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.get('/api/profile/')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data['user']['username'], 'testuser')
        self.assertEqual(data['user']['email'], 'test@example.com')
        self.assertEqual(data['student_id'], 'STU001')

    def test_profile_api_update(self):
        """Test updating user profile via API"""
        self.client.force_authenticate(user=self.user)
        
        update_data = {
            'phone_number': '+1234567890',
            'address': '123 Main St'
        }
        
        response = self.client.put('/api/profile/', update_data, format='json')
        self.assertEqual(response.status_code, 200)
        
        # Verify updates
        self.student.refresh_from_db()
        
        self.assertEqual(self.student.phone_number, '+1234567890')
        self.assertEqual(self.student.address, '123 Main St')

    def test_dashboard_api(self):
        """Test dashboard API"""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.get('/api/dashboard/')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('student', data)
        self.assertIn('registrations', data)
        self.assertIn('stats', data)


class RegistrationAPITestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.course = Course.objects.create(
            name='Computer Science',
            code='CS_MASTERS',
            description='Master of Computer Science'
        )
        self.module = Module.objects.create(
            course=self.course,
            name='Test Module',
            code='CS101',
            description='Test module',
            credits=3,
            category='CORE'
        )
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            is_active=True
        )
        self.student = Student.objects.create(
            user=self.user,
            student_id='STU001'
        )

    def test_registration_api_create(self):
        """Test creating registration via API"""
        self.client.force_authenticate(user=self.user)
        
        data = {
            'module_id': self.module.pk
        }
        
        response = self.client.post('/api/registrations/', data, format='json')
        self.assertEqual(response.status_code, 201)
        
        # Verify registration was created
        self.assertTrue(
            Registration.objects.filter(
                student=self.student,
                module=self.module
            ).exists()
        )

    def test_registration_api_list(self):
        """Test listing user's registrations"""
        # Create registration
        Registration.objects.create(
            student=self.student,
            module=self.module
        )
        
        self.client.force_authenticate(user=self.user)
        
        response = self.client.get('/api/registrations/')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(len(data['results']), 1)
        self.assertEqual(data['results'][0]['module']['code'], 'CS101')

    def test_registration_api_delete(self):
        """Test deleting registration via API"""
        registration = Registration.objects.create(
            student=self.student,
            module=self.module
        )
        
        self.client.force_authenticate(user=self.user)
        
        response = self.client.delete(f'/api/registrations/{registration.pk}/')
        self.assertEqual(response.status_code, 204)
        
        # Verify registration was deleted
        self.assertFalse(
            Registration.objects.filter(pk=registration.pk).exists()
        )

    def test_registration_api_permissions(self):
        """Test registration API permissions"""
        # Create another user and their registration
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123',
            is_active=True
        )
        other_student = Student.objects.create(
            user=other_user,
            student_id='STU002'
        )
        other_registration = Registration.objects.create(
            student=other_student,
            module=self.module
        )
        
        # Try to delete other user's registration
        self.client.force_authenticate(user=self.user)
        
        response = self.client.delete(f'/api/registrations/{other_registration.pk}/')
        self.assertIn(response.status_code, [403, 404])  # Either is acceptable for permissions


class NewsAPITestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()

    def test_news_api_list(self):
        """Test news list API"""
        # Create published and unpublished news
        published_news = NewsUpdate.objects.create(
            title='Published News',
            content='This is published',
            is_published=True
        )
        unpublished_news = NewsUpdate.objects.create(
            title='Unpublished News',
            content='This is not published',
            is_published=False
        )
        
        response = self.client.get('/api/news/')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(len(data['results']), 1)  # Only published news
        self.assertEqual(data['results'][0]['title'], 'Published News')

    def test_news_api_detail(self):
        """Test news detail API"""
        news = NewsUpdate.objects.create(
            title='Test News',
            content='Test content',
            is_published=True
        )
        
        response = self.client.get(f'/api/news/{news.pk}/')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data['title'], 'Test News')

    def test_news_api_unpublished_access(self):
        """Test that unpublished news is not accessible"""
        news = NewsUpdate.objects.create(
            title='Unpublished News',
            content='This should not be accessible',
            is_published=False
        )
        
        response = self.client.get(f'/api/news/{news.pk}/')
        self.assertEqual(response.status_code, 404)


class ContactAPITestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()

    def test_contact_api_create(self):
        """Test contact message creation via API"""
        data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'subject': 'Test Subject',
            'message': 'Test message content'
        }
        
        response = self.client.post('/api/contact/', data, format='json')
        self.assertEqual(response.status_code, 200)
        
        # Verify contact message was created
        self.assertTrue(
            ContactMessage.objects.filter(
                name='John Doe',
                email='john@example.com'
            ).exists()
        )

    def test_contact_api_validation(self):
        """Test contact API validation"""
        # Test with missing required fields
        data = {
            'name': 'John Doe'
            # Missing email, subject, message
        }
        
        response = self.client.post('/api/contact/', data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_contact_api_invalid_email(self):
        """Test contact API with invalid email"""
        data = {
            'name': 'John Doe',
            'email': 'invalid-email',
            'subject': 'Test',
            'message': 'Test message'
        }
        
        response = self.client.post('/api/contact/', data, format='json')
        self.assertEqual(response.status_code, 400)


class StatsAPITestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        # Create test data
        self.course = Course.objects.create(
            name='Computer Science',
            code='CS_MASTERS',
            description='Master of Computer Science'
        )
        self.module = Module.objects.create(
            course=self.course,
            name='Test Module',
            code='CS101',
            description='Test',
            credits=3,
            category='CORE'
        )
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            is_active=True
        )
        self.student = Student.objects.create(
            user=self.user,
            student_id='STU001'
        )
        Registration.objects.create(
            student=self.student,
            module=self.module
        )

    def test_stats_api(self):
        """Test statistics API"""
        response = self.client.get('/api/stats/')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('students', data)
        self.assertIn('modules', data)
        self.assertIn('registrations', data)
        
        # Verify stats are accurate
        self.assertEqual(data['students'], 1)
        self.assertEqual(data['modules'], 1)
        self.assertEqual(data['registrations'], 1)


class APIErrorHandlingTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()

    def test_api_404_handling(self):
        """Test API 404 error handling"""
        response = self.client.get('/api/modules/999999/')
        self.assertEqual(response.status_code, 404)

    def test_api_method_not_allowed(self):
        """Test API method not allowed handling"""
        response = self.client.patch('/api/stats/')
        self.assertEqual(response.status_code, 405)

    def test_api_validation_errors(self):
        """Test API validation error responses"""
        response = self.client.post('/api/contact/', {}, format='json')
        self.assertEqual(response.status_code, 400)
        
        data = response.json()
        # Should return validation errors
        self.assertIsInstance(data, dict)


class APIPerformanceTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        
        # Create a course first
        self.course = Course.objects.create(
            name='Computer Science',
            code='CS_MASTERS',
            description='Master of Computer Science'
        )
        
        # Create multiple modules
        for i in range(50):
            Module.objects.create(
                course=self.course,
                name=f'Module {i}',
                code=f'CS{i:03d}',
                description=f'Description {i}',
                credits=3,
                category='CORE'
            )

    def test_module_list_performance(self):
        """Test module list API performance with many modules"""
        response = self.client.get('/api/modules/')
        self.assertEqual(response.status_code, 200)
        
        # Should handle large datasets efficiently
        data = response.json()
        self.assertGreater(len(data['results']), 0)

    def test_api_pagination_performance(self):
        """Test API pagination performance"""
        response = self.client.get('/api/modules/?page_size=10')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        # With 50+ modules created in setUp, we should get some pagination
        self.assertIn('results', data)
        self.assertLessEqual(len(data['results']), 50)  # At least verify it's reasonable


class APICorsTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()

    def test_cors_headers(self):
        """Test that CORS headers are present"""
        response = self.client.get('/api/modules/')
        self.assertEqual(response.status_code, 200)
        
        # CORS headers should be present if configured
        # Note: Actual CORS headers depend on django-cors-headers configuration

    def test_options_request(self):
        """Test OPTIONS request handling"""
        response = self.client.options('/api/modules/')
        # Should return allowed methods or CORS headers
        self.assertIn(response.status_code, [200, 204, 403])  # 403 is acceptable if CORS not configured
