from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from modules.models import Course, Module
from students.models import Student
from registrations.models import Registration
from portalcontent.models import SiteConfiguration, NewsUpdate
from accounts.models import ContactMessage
import random


class Command(BaseCommand):
    help = 'Load initial seed data for the university system'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting to load seed data...'))
        
        # Create site configuration
        self.create_site_config()
        
        # Create sample courses
        self.create_courses()
        
        # Create sample modules
        self.create_modules()
        
        # Create sample users and students
        self.create_users_and_students()
        
        # Create sample registrations
        self.create_registrations()
        
        # Create sample news updates
        self.create_news_updates()
        
        # Create sample contact messages
        self.create_contact_messages()
        
        self.stdout.write(self.style.SUCCESS('Successfully loaded seed data!'))

    def create_site_config(self):
        """Create site configuration if it doesn't exist"""
        if not SiteConfiguration.objects.exists():
            config = SiteConfiguration.objects.create(
                site_name="University Module Registration System",
                site_description="Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                contact_email="info@university.edu",
                contact_phone="+1-555-123-4567",
                address="123 University Ave, Academic City, State 12345",
                about_content="Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.",
                is_active=True
            )
            self.stdout.write(f'Created site configuration: {config.site_name}')

    def create_courses(self):
        """Create sample courses"""
        courses_data = [
            {
                'code': 'CS_DEGREE',
                'name': 'Bachelor of Computer Science',
                'description': 'A comprehensive undergraduate program covering all aspects of computer science including programming, algorithms, databases, and software engineering.',
                'image_url': 'https://images.unsplash.com/photo-1517077304055-6e89abbf09b0?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80',
            },
            {
                'code': 'MATH_DEGREE',
                'name': 'Bachelor of Mathematics',
                'description': 'An undergraduate program focused on pure and applied mathematics, providing a strong foundation in mathematical theory and problem-solving.',
                'image_url': 'https://images.unsplash.com/photo-1635070041078-e363dbe005cb?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80',
            },
            {
                'code': 'ENG_DEGREE',
                'name': 'Bachelor of English Literature',
                'description': 'An undergraduate program exploring literature, writing, and critical analysis across various periods and genres.',
                'image_url': 'https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80',
            },
            {
                'code': 'PHYS_DEGREE',
                'name': 'Bachelor of Physics',
                'description': 'An undergraduate program covering fundamental physics principles from mechanics to quantum physics.',
                'image_url': 'https://images.unsplash.com/photo-1636466497217-26a8cbeaf0aa?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80',
            },
            {
                'code': 'BIO_DEGREE',
                'name': 'Bachelor of Biology',
                'description': 'An undergraduate program exploring life sciences, ecology, genetics, and molecular biology.',
                'image_url': 'https://images.unsplash.com/photo-1578662996442-48f60103fc96?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80',
            },
            {
                'code': 'CHEM_DEGREE',
                'name': 'Bachelor of Chemistry',
                'description': 'An undergraduate program focusing on chemical principles, reactions, and laboratory techniques.',
                'image_url': 'https://images.unsplash.com/photo-1518674660708-0e2c0473e68e?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80',
            },
            {
                'code': 'ECON_DEGREE',
                'name': 'Bachelor of Economics',
                'description': 'An undergraduate program studying economic theory, market analysis, and financial systems.',
                'image_url': 'https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80',
            },
            {
                'code': 'PSYCH_DEGREE',
                'name': 'Bachelor of Psychology',
                'description': 'An undergraduate program exploring human behavior, cognition, and mental processes.',
                'image_url': 'https://images.unsplash.com/photo-1559757148-5c350d0d3c56?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80',
            },
            {
                'code': 'CS_MASTERS',
                'name': 'Master of Computer Science',
                'description': 'An advanced postgraduate program focusing on specialized areas like machine learning, artificial intelligence, and advanced software development.',
                'image_url': 'https://images.unsplash.com/photo-1677442136019-21780ecad995?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80',
            },
            {
                'code': 'MBA_DEGREE',
                'name': 'Master of Business Administration',
                'description': 'A graduate program in business management covering leadership, strategy, finance, and operations.',
                'image_url': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80',
            },
            {
                'code': 'WEB_CERT',
                'name': 'Web Development Certificate',
                'description': 'A certificate program covering modern web development technologies including HTML, CSS, JavaScript, and popular frameworks.',
                'image_url': 'https://images.unsplash.com/photo-1461749280684-dccba630e2f6?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80',
            },
            {
                'code': 'DATA_CERT',
                'name': 'Data Science Certificate',
                'description': 'A certificate program focusing on data analysis, statistics, machine learning, and data visualization.',
                'image_url': 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80',
            },
        ]
        
        for course_data in courses_data:
            course, created = Course.objects.get_or_create(
                code=course_data['code'],
                defaults=course_data
            )
            if created:
                self.stdout.write(f'Created course: {course.code} - {course.name}')

    def create_modules(self):
        """Create sample modules and associate them with courses"""
        # Get courses
        cs_degree = Course.objects.get(code='CS_DEGREE')
        math_degree = Course.objects.get(code='MATH_DEGREE')
        eng_degree = Course.objects.get(code='ENG_DEGREE')
        phys_degree = Course.objects.get(code='PHYS_DEGREE')
        bio_degree = Course.objects.get(code='BIO_DEGREE')
        chem_degree = Course.objects.get(code='CHEM_DEGREE')
        econ_degree = Course.objects.get(code='ECON_DEGREE')
        psych_degree = Course.objects.get(code='PSYCH_DEGREE')
        cs_masters = Course.objects.get(code='CS_MASTERS')
        mba_degree = Course.objects.get(code='MBA_DEGREE')
        web_cert = Course.objects.get(code='WEB_CERT')
        data_cert = Course.objects.get(code='DATA_CERT')
        
        modules_data = [
            # Computer Science Degree Modules
            {
                'course': cs_degree,
                'code': 'CS101',
                'name': 'Introduction to Computer Science',
                'description': 'Fundamental concepts of computer science including problem-solving, algorithms, and basic programming.',
                'image_url': 'https://images.unsplash.com/photo-1481627834876-b7833e8f5570?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80',
                'credits': 3,
                'category': 'CORE'
            },
            {
                'course': cs_degree,
                'code': 'CS201',
                'name': 'Data Structures and Algorithms',
                'description': 'Advanced programming concepts including data structures, algorithm design, and complexity analysis.',
                'image_url': 'https://images.unsplash.com/photo-1434030216411-0b793f4b4173?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80',
                'credits': 4,
                'category': 'CORE'
            },
            {
                'course': cs_degree,
                'code': 'CS301',
                'name': 'Database Systems',
                'description': 'Database design, SQL, normalization, and modern database technologies.',
                'image_url': 'https://images.unsplash.com/photo-1460925895917-afdab827c52f?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80',
                'credits': 3,
                'category': 'CORE',
            },
            {
                'course': cs_degree,
                'code': 'CS302',
                'name': 'Software Engineering',
                'description': 'Software development lifecycle, project management, and modern development practices.',
                'image_url': 'https://images.unsplash.com/photo-1522202176988-66273c2fd55f?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80',
                'credits': 3,
                'category': 'CORE',
            },
            
            # Mathematics Degree Modules
            {
                'course': math_degree,
                'code': 'MATH101',
                'name': 'Calculus I',
                'description': 'Differential and integral calculus, limits, derivatives, and applications.',
                'image_url': 'https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80',
                'credits': 4,
                'category': 'CORE',
            },
            {
                'course': math_degree,
                'code': 'MATH201',
                'name': 'Linear Algebra',
                'description': 'Vector spaces, matrices, eigenvalues, and linear transformations.',
                'image_url': 'https://images.unsplash.com/photo-1635070041078-e363dbe005cb?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80',
                'credits': 3,
                'category': 'CORE',
            },
            {
                'course': math_degree,
                'code': 'MATH301',
                'name': 'Abstract Algebra',
                'description': 'Groups, rings, fields, and algebraic structures.',
                'image_url': 'https://images.unsplash.com/photo-1596495577886-d920f1fb7238?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80',
                'credits': 3,
                'category': 'SPECIALIZED',
            },
            
            # English Literature Degree Modules
            {
                'course': eng_degree,
                'code': 'ENG101',
                'name': 'Academic Writing',
                'description': 'Essential writing skills for academic and professional contexts.',
                'image_url': 'https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80',
                'credits': 3,
                'category': 'CORE',
            },
            {
                'course': eng_degree,
                'code': 'ENG201',
                'name': 'British Literature',
                'description': 'Survey of British literature from medieval times to the present.',
                'image_url': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80',
                'credits': 3,
                'category': 'CORE',
            },
            {
                'course': eng_degree,
                'code': 'ENG301',
                'name': 'Creative Writing',
                'description': 'Fiction, poetry, and creative non-fiction writing workshops.',
                'image_url': 'https://images.unsplash.com/photo-1455390582262-044cdead277a?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80',
                'credits': 3,
                'category': 'ELECTIVE',
            },
            
            # Physics Degree Modules
            {
                'course': phys_degree,
                'code': 'PHYS101',
                'name': 'Physics I',
                'description': 'Classical mechanics, thermodynamics, and wave phenomena.',
                'image_url': 'https://images.unsplash.com/photo-1636466497217-26a8cbeaf0aa?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80',
                'credits': 4,
                'category': 'CORE',
            },
            {
                'course': phys_degree,
                'code': 'PHYS201',
                'name': 'Modern Physics',
                'description': 'Quantum mechanics, relativity, and atomic physics.',
                'image_url': 'https://images.unsplash.com/photo-1614728263952-84ea256f9679?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80',
                'credits': 4,
                'category': 'CORE',
            },
            {
                'course': phys_degree,
                'code': 'PHYS301',
                'name': 'Quantum Mechanics',
                'description': 'Advanced quantum theory and applications.',
                'image_url': 'https://images.unsplash.com/photo-1635070041078-e363dbe005cb?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80',
                'credits': 4,
                'category': 'SPECIALIZED',
            },
            
            # Biology Degree Modules
            {
                'course': bio_degree,
                'code': 'BIO101',
                'name': 'General Biology',
                'description': 'Introduction to cell biology, genetics, and evolution.',
                'image_url': 'https://images.unsplash.com/photo-1578662996442-48f60103fc96?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80',
                'credits': 4,
                'category': 'CORE',
            },
            {
                'course': bio_degree,
                'code': 'BIO201',
                'name': 'Ecology',
                'description': 'Study of ecosystems, biodiversity, and environmental interactions.',
                'image_url': 'https://images.unsplash.com/photo-1441974231531-c6227db76b6e?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80',
                'credits': 3,
                'category': 'CORE',
            },
            {
                'course': bio_degree,
                'code': 'BIO301',
                'name': 'Molecular Biology',
                'description': 'DNA, RNA, protein synthesis, and genetic engineering.',
                'image_url': 'https://images.unsplash.com/photo-1507413245164-6160d8298b31?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80',
                'credits': 4,
                'category': 'SPECIALIZED',
            },
            
            # Chemistry Degree Modules
            {
                'course': chem_degree,
                'code': 'CHEM101',
                'name': 'General Chemistry',
                'description': 'Atomic structure, bonding, and basic chemical reactions.',
                'image_url': 'https://images.unsplash.com/photo-1518674660708-0e2c0473e68e?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80',
                'credits': 4,
                'category': 'CORE',
            },
            {
                'course': chem_degree,
                'code': 'CHEM201',
                'name': 'Organic Chemistry',
                'description': 'Carbon-based compounds, reactions, and synthesis.',
                'image_url': 'https://images.unsplash.com/photo-1532634993-15f421e42ec0?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80',
                'credits': 4,
                'category': 'CORE',
            },
            
            # Economics Degree Modules
            {
                'course': econ_degree,
                'code': 'ECON101',
                'name': 'Microeconomics',
                'description': 'Individual markets, supply and demand, and consumer behavior.',
                'image_url': 'https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80',
                'credits': 3,
                'category': 'CORE',
            },
            {
                'course': econ_degree,
                'code': 'ECON201',
                'name': 'Macroeconomics',
                'description': 'National economy, GDP, inflation, and monetary policy.',
                'image_url': 'https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80',
                'credits': 3,
                'category': 'CORE',
            },
            
            # Psychology Degree Modules
            {
                'course': psych_degree,
                'code': 'PSYC101',
                'name': 'Introduction to Psychology',
                'description': 'Basic principles of human behavior and mental processes.',
                'image_url': 'https://images.unsplash.com/photo-1559757148-5c350d0d3c56?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80',
                'credits': 3,
                'category': 'CORE',
            },
            {
                'course': psych_degree,
                'code': 'PSYC201',
                'name': 'Developmental Psychology',
                'description': 'Human development from infancy through adulthood.',
                'image_url': 'https://images.unsplash.com/photo-1569173112611-de575ffb06d8?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80',
                'credits': 3,
                'category': 'CORE',
            },
            
            # Masters Computer Science Modules
            {
                'course': cs_masters,
                'code': 'CS501',
                'name': 'Machine Learning',
                'description': 'Advanced machine learning algorithms, neural networks, and AI applications.',
                'image_url': 'https://images.unsplash.com/photo-1677442136019-21780ecad995?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80',
                'credits': 3,
                'category': 'SPECIALIZED',
            },
            {
                'course': cs_masters,
                'code': 'CS502',
                'name': 'Advanced Algorithms',
                'description': 'Complex algorithm design, optimization, and computational complexity.',
                'image_url': 'https://images.unsplash.com/photo-1518186285589-2f7649de83e0?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80',
                'credits': 3,
                'category': 'SPECIALIZED',
            },
            
            # MBA Degree Modules
            {
                'course': mba_degree,
                'code': 'MBA501',
                'name': 'Strategic Management',
                'description': 'Business strategy, competitive analysis, and organizational leadership.',
                'image_url': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80',
                'credits': 3,
                'category': 'CORE',
            },
            {
                'course': mba_degree,
                'code': 'MBA502',
                'name': 'Financial Management',
                'description': 'Corporate finance, investment analysis, and financial planning.',
                'image_url': 'https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80',
                'credits': 3,
                'category': 'CORE',
            },
            
            # Web Development Certificate Modules
            {
                'course': web_cert,
                'code': 'WEB101',
                'name': 'HTML & CSS Fundamentals',
                'description': 'Basic web markup and styling using HTML5 and CSS3.',
                'image_url': 'https://images.unsplash.com/photo-1461749280684-dccba630e2f6?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80',
                'credits': 2,
                'category': 'CORE',
            },
            {
                'course': web_cert,
                'code': 'WEB201',
                'name': 'JavaScript Programming',
                'description': 'Client-side programming with JavaScript and modern frameworks.',
                'image_url': 'https://images.unsplash.com/photo-1579468118864-1b9ea3c0db4a?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80',
                'credits': 3,
                'category': 'CORE',
            },
            {
                'course': web_cert,
                'code': 'WEB301',
                'name': 'React Development',
                'description': 'Modern web development using React.js and component-based architecture.',
                'image_url': 'https://images.unsplash.com/photo-1633356122544-f134324a6cee?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80',
                'credits': 3,
                'category': 'SPECIALIZED',
            },
            
            # Data Science Certificate Modules
            {
                'course': data_cert,
                'code': 'DATA101',
                'name': 'Introduction to Data Science',
                'description': 'Data analysis fundamentals, statistics, and Python programming.',
                'image_url': 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80',
                'credits': 3,
                'category': 'CORE',
            },
            {
                'course': data_cert,
                'code': 'DATA201',
                'name': 'Data Visualization',
                'description': 'Creating effective charts, graphs, and interactive visualizations.',
                'image_url': 'https://images.unsplash.com/photo-1460925895917-afdab827c52f?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80',
                'credits': 3,
                'category': 'CORE',
            },
            {
                'course': data_cert,
                'code': 'DATA301',
                'name': 'Machine Learning for Data Science',
                'description': 'Applying ML algorithms to real-world data problems.',
                'image_url': 'https://images.unsplash.com/photo-1555949963-aa79dcee981c?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80',
                'credits': 4,
                'category': 'SPECIALIZED',
            },
        ]
        
        for module_data in modules_data:
            module, created = Module.objects.get_or_create(
                code=module_data['code'],
                defaults=module_data
            )
            if created:
                self.stdout.write(f'Created module: {module.code} - {module.name} (Course: {module.course.code})')

    def create_users_and_students(self):
        """Create sample users and students"""
        students_data = [
            {
                'username': 'john_doe',
                'email': 'john.doe@student.university.edu',
                'first_name': 'John',
                'last_name': 'Doe',
                'password': 'student123',
                'phone_number': '+1-555-001-0001',
                'address': '123 Student St, Campus City, State 12345'
            },
            {
                'username': 'jane_smith',
                'email': 'jane.smith@student.university.edu',
                'first_name': 'Jane',
                'last_name': 'Smith',
                'password': 'student123',
                'phone_number': '+1-555-001-0002',
                'address': '456 University Ave, Campus City, State 12345'
            },
            {
                'username': 'mike_johnson',
                'email': 'mike.johnson@student.university.edu',
                'first_name': 'Mike',
                'last_name': 'Johnson',
                'password': 'student123',
                'phone_number': '+1-555-001-0003',
                'address': '789 Academic Blvd, Campus City, State 12345'
            },
            {
                'username': 'sarah_wilson',
                'email': 'sarah.wilson@student.university.edu',
                'first_name': 'Sarah',
                'last_name': 'Wilson',
                'password': 'student123',
                'phone_number': '+1-555-001-0004',
                'address': '321 Scholar Lane, Campus City, State 12345'
            },
        ]
        
        for student_data in students_data:
            user, created = User.objects.get_or_create(
                username=student_data['username'],
                defaults={
                    'email': student_data['email'],
                    'first_name': student_data['first_name'],
                    'last_name': student_data['last_name'],
                    'is_active': True
                }
            )
            if created:
                user.set_password(student_data['password'])
                user.save()
                self.stdout.write(f'Created user: {user.username}')
            
            student, created = Student.objects.get_or_create(
                user=user,
                defaults={
                    'phone_number': student_data['phone_number'],
                    'address': student_data['address']
                }
            )
            if created:
                self.stdout.write(f'Created student: {student.student_id}')

    def create_registrations(self):
        """Create sample registrations"""
        students = Student.objects.all()
        modules = Module.objects.all()
        statuses = ['enrolled', 'completed', 'pending']
        
        # Create random registrations
        for student in students:
            # Each student registers for 2-4 random modules
            num_registrations = random.randint(2, 4)
            selected_modules = random.sample(list(modules), min(num_registrations, len(modules)))
            
            for module in selected_modules:
                registration, created = Registration.objects.get_or_create(
                    student=student,
                    module=module,
                    defaults={
                        'status': random.choice(statuses),
                        'grade': random.choice(['A', 'B', 'C', 'D', '']) if random.choice([True, False]) else ''
                    }
                )
                if created:
                    self.stdout.write(f'Created registration: {student.user.username} -> {module.code}')

    def create_news_updates(self):
        """Create sample news updates"""
        news_data = [
            {
                'title': 'Welcome to Fall 2024 Semester',
                'content': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris.',
                'is_published': True
            },
            {
                'title': 'New Computer Science Course Added',
                'content': 'Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim.',
                'is_published': True
            },
            {
                'title': 'Campus Library Extended Hours',
                'content': 'Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam, eaque ipsa quae ab illo inventore veritatis.',
                'is_published': True
            },
            {
                'title': 'Spring 2025 Registration Opens Soon',
                'content': 'Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit, sed quia consequuntur magni dolores eos qui ratione voluptatem sequi nesciunt.',
                'is_published': False
            },
        ]
        
        for news_item in news_data:
            news, created = NewsUpdate.objects.get_or_create(
                title=news_item['title'],
                defaults=news_item
            )
            if created:
                self.stdout.write(f'Created news update: {news.title}')

    def create_contact_messages(self):
        """Create sample contact messages"""
        messages_data = [
            {
                'name': 'Alex Thompson',
                'email': 'alex.thompson@email.com',
                'subject': 'Question about course prerequisites',
                'message': 'I would like to know more about the prerequisites for the Master of Computer Science course. Could you please provide more information?',
                'is_read': False
            },
            {
                'name': 'Emily Chen',
                'email': 'emily.chen@email.com',
                'subject': 'Registration deadline inquiry',
                'message': 'What is the deadline for course registration for the current semester? I want to make sure I don\'t miss it.',
                'is_read': True
            },
            {
                'name': 'David Rodriguez',
                'email': 'david.rodriguez@email.com',
                'subject': 'Technical support needed',
                'message': 'I am having trouble accessing my student dashboard. Could someone help me resolve this issue?',
                'is_read': False
            },
        ]
        
        for message_data in messages_data:
            message, created = ContactMessage.objects.get_or_create(
                email=message_data['email'],
                subject=message_data['subject'],
                defaults=message_data
            )
            if created:
                self.stdout.write(f'Created contact message: {message.subject}')
