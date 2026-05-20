from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core import mail
from django.utils import timezone
from datetime import timedelta
import json
from accounts.models import OTPVerification, ContactMessage


class AccountsBasicTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.test_user_data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'TestPass123!',
            'first_name': 'Test',
            'last_name': 'User'
        }

    def test_contact_message_creation(self):
        """Test creating a contact message"""
        message = ContactMessage.objects.create(
            name='Test User',
            email='test@example.com',
            subject='Test Subject',
            message='This is a test message'
        )
        
        self.assertEqual(str(message), 'Test User - Test Subject')
        self.assertFalse(message.is_read)

    def test_otp_verification_creation(self):
        """Test creating an OTP verification"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        otp = OTPVerification.objects.create(
            user=user,
            otp_code='123456',
            otp_type='REGISTER'
        )
        
        self.assertEqual(otp.otp_code, '123456')
        self.assertEqual(otp.otp_type, 'REGISTER')
        self.assertFalse(otp.is_used)


class AccountsViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_register_page_renders(self):
        """Test that register page renders correctly"""
        response = self.client.get(reverse('accounts:register'))
        self.assertEqual(response.status_code, 200)

    def test_login_page_renders(self):
        """Test that login page renders correctly"""
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200)

    def test_verify_otp_page_renders(self):
        """Test that verify OTP page renders correctly"""
        # Create a test user first
        user = User.objects.create_user(username='testuser', email='test@example.com', password='testpass123')
        # Create an OTP for the user
        from .models import OTPVerification
        from django.utils import timezone
        otp = OTPVerification.objects.create(
            user=user,
            otp_code='123456',
            otp_type='REGISTER',
            expires_at=timezone.now() + timezone.timedelta(minutes=15)
        )
        response = self.client.get(reverse('accounts:verify_otp', kwargs={'user_id': user.id}))
        self.assertEqual(response.status_code, 200)
