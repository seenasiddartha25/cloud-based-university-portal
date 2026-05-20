from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from modules.models import Module, Course
from students.models import Student
from registrations.models import Registration


class ModulesTestCase(TestCase):
    def setUp(self):
        self.client = Client()
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

    def test_module_list_public_access(self):
        """Test that module list is publicly accessible"""
        response = self.client.get('/api/modules/')
        self.assertEqual(response.status_code, 200)

    def test_module_detail_public_access(self):
        """Test that module detail is publicly accessible"""
        response = self.client.get(f'/api/modules/{self.module.pk}/')
        self.assertEqual(response.status_code, 200)


class ModuleModelTestCase(TestCase):
    def test_module_creation(self):
        """Test creating a module"""
        course = Course.objects.create(
            name='Computer Science',
            code='CS_MASTERS',
            description='Master of Computer Science'
        )
        module = Module.objects.create(
            course=course,
            name='Data Structures',
            code='CS201',
            description='Study of data structures',
            credits=4,
            category='CORE'
        )
        
        self.assertEqual(str(module), 'CS201 - Data Structures')
        self.assertEqual(module.credits, 4)

    def test_module_slug_generation(self):
        """Test that module code works as slug"""
        course = Course.objects.create(
            name='Computer Science',
            code='CS_MASTERS',
            description='Master of Computer Science'
        )
        module = Module.objects.create(
            course=course,
            name='Advanced Data Structures',
            code='CS301',
            description='Advanced study of data structures',
            credits=4,
            category='CORE'
        )
        
        self.assertEqual(module.code, 'CS301')


class ModuleViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.course = Course.objects.create(
            name='Computer Science',
            code='CS_MASTERS',
            description='Master of Computer Science'
        )
        self.module = Module.objects.create(
            course=self.course,
            name='Test Module',
            code='CS101',
            description='Test module description',
            credits=3,
            category='CORE'
        )

    def test_module_list_page_renders(self):
        """Test that module list page renders correctly"""
        response = self.client.get(reverse('modules:module_list'))
        self.assertEqual(response.status_code, 200)

    def test_module_detail_page_renders(self):
        """Test that module detail page renders correctly"""
        response = self.client.get(reverse('modules:module_detail', args=[self.module.code]))
        self.assertEqual(response.status_code, 200)
