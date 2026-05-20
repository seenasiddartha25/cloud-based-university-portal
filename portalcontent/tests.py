from django.test import TestCase, Client
from django.urls import reverse
from django.core import mail
from portalcontent.models import SiteConfiguration, NewsUpdate
from accounts.models import ContactMessage


class PortalcontentTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_home_page_renders(self):
        """Test that home page renders correctly"""
        response = self.client.get(reverse('portalcontent:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'University')

    def test_about_page_renders(self):
        """Test that about page renders correctly"""
        response = self.client.get(reverse('portalcontent:about'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'About')

    def test_contact_page_renders(self):
        """Test that contact page renders correctly"""
        response = self.client.get(reverse('portalcontent:contact'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Contact')

    def test_unauthorized_page_renders(self):
        """Test that unauthorized page renders correctly"""
        response = self.client.get(reverse('portalcontent:unauthorized'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Access Denied')

    def test_site_configuration_singleton(self):
        """Test that SiteConfiguration enforces singleton pattern"""
        # First configuration should work
        config1 = SiteConfiguration.objects.create(
            site_name='Test University',
            site_description='Test description',
            contact_email='test@example.com'
        )
        self.assertEqual(SiteConfiguration.objects.count(), 1)
        
        # Second configuration should raise an error
        with self.assertRaises(ValueError):
            config2 = SiteConfiguration.objects.create(
                site_name='Another University',
                site_description='Another description',
                contact_email='another@example.com'
            )

    def test_site_configuration_get_method(self):
        """Test that get_site_config creates config if it doesn't exist"""
        # No configurations exist yet
        self.assertEqual(SiteConfiguration.objects.count(), 0)
        
        # get_site_config should create one
        config = SiteConfiguration.get_site_config()
        self.assertEqual(SiteConfiguration.objects.count(), 1)
        self.assertEqual(config.site_name, 'University Module Registration')
        
        # Calling it again should return the same one
        config2 = SiteConfiguration.get_site_config()
        self.assertEqual(SiteConfiguration.objects.count(), 1)
        self.assertEqual(config.id, config2.id)

    def test_news_update_slug_generation(self):
        """Test that NewsUpdate automatically generates slugs"""
        news = NewsUpdate.objects.create(
            title='Test News Item',
            content='This is a test news item.'
        )
        self.assertEqual(news.slug, 'test-news-item')
        
        # Test duplicate title creates unique slug
        news2 = NewsUpdate.objects.create(
            title='Test News Item',
            content='This is another test news item.'
        )
        self.assertEqual(news2.slug, 'test-news-item-1')

    def test_published_news_manager(self):
        """Test that published manager only returns published news"""
        # Create some news items
        news1 = NewsUpdate.objects.create(
            title='Published News',
            content='This is published.',
            is_published=True
        )
        news2 = NewsUpdate.objects.create(
            title='Unpublished News',
            content='This is not published.',
            is_published=False
        )
        
        # Check that published manager filters correctly
        self.assertEqual(NewsUpdate.objects.count(), 2)
        self.assertEqual(NewsUpdate.published.count(), 1)
        self.assertEqual(NewsUpdate.published.first().title, 'Published News')

    def test_contact_form_submission(self):
        """Test contact form submission creates a ContactMessage"""
        # Post to the contact form
        response = self.client.post(
            reverse('portalcontent:contact'),
            {
                'name': 'Test User',
                'email': 'test@example.com',
                'subject': 'Test Subject',
                'message': 'This is a test message.',
                'phone': '123-456-7890'
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'  # Simulate AJAX request
        )
        
        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {'success': True, 'message': 'Thank you! Your message has been sent successfully.'}
        )
        
        # Check that a ContactMessage was created
        self.assertEqual(ContactMessage.objects.count(), 1)
        message = ContactMessage.objects.first()
        self.assertEqual(message.name, 'Test User')
        self.assertEqual(message.email, 'test@example.com')
        self.assertEqual(message.subject, 'Test Subject')
        self.assertEqual(message.message, 'This is a test message.')
        self.assertEqual(message.phone, '123-456-7890')

    def test_contact_form_validation(self):
        """Test contact form validation"""
        # Post with missing fields
        response = self.client.post(
            reverse('portalcontent:contact'),
            {
                'name': 'Test User',
                # email missing
                'subject': 'Test Subject',
                'message': 'This is a test message.'
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'  # Simulate AJAX request
        )
        
        # Check response indicates failure
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {'success': False, 'message': 'All fields are required.'}
        )
        
        # No message should have been created
        self.assertEqual(ContactMessage.objects.count(), 0)


class PortalcontentIntegrationTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Create site configuration
        self.config = SiteConfiguration.objects.create(
            site_name='Test University',
            site_description='Test description',
            contact_email='test@example.com',
            contact_phone='+1-234-567-8900',
            address='123 Test St, Test City',
            about_content='This is the about content.'
        )
        
        # Create some news items
        self.news1 = NewsUpdate.objects.create(
            title='First News Item',
            content='First news content',
            is_published=True
        )
        self.news2 = NewsUpdate.objects.create(
            title='Second News Item',
            content='Second news content',
            is_published=True
        )
        self.news3 = NewsUpdate.objects.create(
            title='Unpublished News',
            content='Hidden content',
            is_published=False
        )
    
    def test_home_page_shows_site_config(self):
        """Test that home page uses site configuration"""
        response = self.client.get(reverse('portalcontent:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test University')
        self.assertContains(response, 'Test description')
    
    def test_home_page_shows_news(self):
        """Test that home page shows published news"""
        response = self.client.get(reverse('portalcontent:home'))
        self.assertEqual(response.status_code, 200)
        
        # Published news should appear
        self.assertContains(response, 'First News Item')
        self.assertContains(response, 'Second News Item')
        
        # Unpublished news should not appear
        self.assertNotContains(response, 'Unpublished News')
    
    def test_about_page_shows_content(self):
        """Test that about page shows content from site configuration"""
        response = self.client.get(reverse('portalcontent:about'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This is the about content.')
    
    def test_contact_page_shows_info(self):
        """Test that contact page shows contact info from site configuration"""
        response = self.client.get(reverse('portalcontent:contact'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'test@example.com')
        self.assertContains(response, '+1-234-567-8900')
        self.assertContains(response, '123 Test St, Test City')
