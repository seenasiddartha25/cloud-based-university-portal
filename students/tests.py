from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from students.models import Student
import tempfile
import os


class StudentsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            is_active=True
        )
        self.student = Student.objects.create(
            user=self.user,
            student_id='STU001',
            date_of_birth='1990-01-01'
        )

    def test_profile_fetch_authenticated(self):
        """Test fetching profile for authenticated user"""
        self.client.force_login(self.user)
        response = self.client.get('/api/profile/')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['user']['username'], 'testuser')
        self.assertEqual(data['student_id'], 'STU001')

    def test_profile_fetch_unauthenticated(self):
        """Test fetching profile for unauthenticated user"""
        response = self.client.get('/api/profile/')
        self.assertEqual(response.status_code, 403)

    def test_profile_update_authenticated(self):
        """Test updating profile for authenticated user"""
        self.client.force_login(self.user)
        
        update_data = {
            'user': {
                'first_name': 'Updated',
                'last_name': 'Name',
                'email': 'updated@example.com'
            },
            'phone_number': '+1234567890',
            'address': '123 Test Street'
        }
        
        response = self.client.put('/api/profile/', 
                                   data=update_data, 
                                   content_type='application/json')
        
        if response.status_code != 200:
            raise AssertionError(f"Status: {response.status_code}, Content: {response.content}")
        self.assertEqual(response.status_code, 200)
        
        # Check updates were applied
        self.user.refresh_from_db()
        self.student.refresh_from_db()
        
        self.assertEqual(self.user.first_name, 'Updated')
        self.assertEqual(self.user.last_name, 'Name')
        self.assertEqual(self.student.phone_number, '+1234567890')

    def test_profile_update_unauthenticated(self):
        """Test updating profile for unauthenticated user"""
        update_data = {
            'first_name': 'Updated',
            'last_name': 'Name'
        }
        
        response = self.client.put('/api/profile/', 
                                   data=update_data, 
                                   content_type='application/json')
        
        self.assertEqual(response.status_code, 403)

    def test_profile_photo_upload(self):
        """Test uploading profile photo"""
        self.client.force_login(self.user)
        
        # Create a temporary image file
        from PIL import Image
        import io
        
        # Create a simple test image in memory
        image = Image.new('RGB', (100, 100), color='red')
        img_io = io.BytesIO()
        image.save(img_io, format='PNG')
        img_io.seek(0)
        
        uploaded_file = SimpleUploadedFile(
            "test_image.png",
            img_io.getvalue(),
            content_type="image/png"
        )
        
        # Use multipart for file upload
        response = self.client.post(
            '/api/profile/photo/',
            {'profile_picture': uploaded_file}
        )
        
        if response.status_code != 200:
            raise AssertionError(f"Status: {response.status_code}, Content: {response.content}")
        self.assertEqual(response.status_code, 200)
        
        # Check photo was uploaded
        self.student.refresh_from_db()
        self.assertTrue(self.student.profile_picture)

    def test_dashboard_data_fetch(self):
        """Test fetching dashboard data"""
        self.client.force_login(self.user)
        response = self.client.get('/api/dashboard/')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('student', data)
        self.assertIn('registrations', data)
        self.assertIn('stats', data)

    def test_my_modules_fetch(self):
        """Test fetching user's modules"""
        self.client.force_login(self.user)
        response = self.client.get('/api/my-modules/')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('modules', data)
        self.assertIn('count', data)
        self.assertIsInstance(data['modules'], list)


class StudentModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_student_creation(self):
        """Test creating a student"""
        from datetime import date
        student = Student.objects.create(
            user=self.user,
            student_id='STU001',
            date_of_birth=date(1990, 1, 1),
            phone_number='+1234567890'
        )
        
        self.assertEqual(str(student), 'testuser (STU001)')
        self.assertEqual(student.full_name, 'testuser')  # Returns username as fallback

    def test_student_full_name(self):
        """Test student full name property"""
        self.user.first_name = 'John'
        self.user.last_name = 'Doe'
        self.user.save()
        
        student = Student.objects.create(
            user=self.user,
            student_id='STU001'
        )
        
        self.assertEqual(student.full_name, 'John Doe')

    def test_student_age_calculation(self):
        """Test student age calculation"""
        from datetime import date
        student = Student.objects.create(
            user=self.user,
            student_id='STU001',
            date_of_birth=date(1990, 1, 1)
        )
        
        # Age will depend on current date, but should be reasonable
        age = student.age
        self.assertIsInstance(age, int)
        self.assertGreater(age, 0)
        self.assertLess(age, 150)


class StudentViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
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

    def test_dashboard_page_renders(self):
        """Test that dashboard page renders correctly"""
        self.client.force_login(self.user)
        response = self.client.get(reverse('students:dashboard'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dashboard')

    def test_dashboard_page_unauthenticated(self):
        """Test dashboard page redirects unauthenticated users"""
        response = self.client.get(reverse('students:dashboard'))
        # Should redirect to login
        self.assertEqual(response.status_code, 302)

    def test_profile_setup_page_renders(self):
        """Test that profile setup page renders correctly"""
        # Create a user without a student profile for this test
        user_without_profile = User.objects.create_user(
            username='newuser',
            email='newuser@example.com',
            password='testpass123',
            is_active=True
        )
        self.client.force_login(user_without_profile)
        response = self.client.get(reverse('students:profile_setup'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Complete Your Profile')

    def test_profile_edit_page_renders(self):
        """Test that profile edit page renders correctly"""
        self.client.force_login(self.user)
        response = self.client.get(reverse('students:profile_edit'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Edit Profile')


class StudentPermissionsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.active_user = User.objects.create_user(
            username='activeuser',
            email='active@example.com',
            password='testpass123',
            is_active=True
        )
        self.inactive_user = User.objects.create_user(
            username='inactiveuser',
            email='inactive@example.com',
            password='testpass123',
            is_active=False
        )
        Student.objects.create(
            user=self.active_user,
            student_id='STU001'
        )

    def test_inactive_user_access_denied(self):
        """Test that inactive users can't access student features"""
        self.client.force_login(self.inactive_user)
        response = self.client.get('/api/profile/')
        
        # Should be denied access
        self.assertIn(response.status_code, [401, 403])

    def test_active_user_access_granted(self):
        """Test that active users can access student features"""
        self.client.force_login(self.active_user)
        response = self.client.get('/api/profile/')
        
        self.assertEqual(response.status_code, 200)
