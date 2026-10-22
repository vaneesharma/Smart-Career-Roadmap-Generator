"""
Custom management command that fills the database with sample data so the
project isn't empty when you demo it. Run it with:

python manage.py seed_data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import Profile
from core.models import (
    CareerPath, Roadmap, RoadmapStage, RoadmapItem,
    LearningResource, SkillTest, Question, Choice, Testimonial,
)


class Command(BaseCommand):
    help = "Fills the database with sample careers, roadmaps, resources, a skill test and testimonials"

    def handle(self, *args, **options):
        self.create_careers_and_roadmaps()
        self.create_resources()
        self.create_skill_test()
        self.create_testimonials()
        self.create_demo_staff_accounts()
        self.stdout.write(self.style.SUCCESS("Sample data created successfully."))

    def create_careers_and_roadmaps(self):
        careers_data = [
            {
                'name': 'Python Developer',
                'description': 'Builds backend systems, automation scripts and APIs using Python.',
                'required_skills': 'python, django, sql, git',
                'average_salary': '₹4 - ₹10 LPA',
            },
            {
                'name': 'Frontend Developer',
                'description': 'Builds the visual, interactive part of websites and web apps.',
                'required_skills': 'html, css, javascript, react',
                'average_salary': '₹3.5 - ₹9 LPA',
            },
            {
                'name': 'Full Stack Developer',
                'description': 'Handles both the frontend and backend of a web application.',
                'required_skills': 'html, css, javascript, python, django, sql',
                'average_salary': '₹5 - ₹12 LPA',
            },
            {
                'name': 'Data Analyst',
                'description': 'Analyses data to find trends and helps businesses make decisions.',
                'required_skills': 'python, sql, excel, statistics',
                'average_salary': '₹4 - ₹9 LPA',
            },
        ]

        for data in careers_data:
            career, _ = CareerPath.objects.get_or_create(name=data['name'], defaults=data)
            roadmap, _ = Roadmap.objects.get_or_create(career=career, defaults={'estimated_duration_months': 6})

            for level, tasks in [
                ('beginner', ['Learn the basics', 'Complete a beginner tutorial', 'Build a small practice project']),
                ('intermediate', ['Learn core frameworks/tools', 'Build a medium sized project', 'Contribute to open source']),
                ('advanced', ['Master advanced concepts', 'Build a portfolio project', 'Prepare for interviews']),
            ]:
                stage, _ = RoadmapStage.objects.get_or_create(
                    roadmap=roadmap, level=level, defaults={'order': ['beginner', 'intermediate', 'advanced'].index(level)}
                )
                for i, task in enumerate(tasks):
                    RoadmapItem.objects.get_or_create(stage=stage, title=f"{career.name}: {task}", defaults={'order': i})

    def create_resources(self):
        resources = [
            ('Automate the Boring Stuff with Python', 'book', 'https://automatetheboringstuff.com/', 'Python'),
            ('Django Official Documentation', 'documentation', 'https://docs.djangoproject.com/', 'Python'),
            ('freeCodeCamp', 'coding_platform', 'https://www.freecodecamp.org/', 'Web Development'),
            ('MDN Web Docs', 'documentation', 'https://developer.mozilla.org/', 'Web Development'),
            ('CS Dojo YouTube Channel', 'youtube', 'https://www.youtube.com/c/CSDojo', 'Programming'),
            ('LeetCode', 'coding_platform', 'https://leetcode.com/', 'Data Structures & Algorithms'),
        ]
        for title, r_type, link, category in resources:
            LearningResource.objects.get_or_create(
                title=title, defaults={'resource_type': r_type, 'link': link, 'category': category}
            )

    def create_skill_test(self):
        test, _ = SkillTest.objects.get_or_create(
            title='Python Basics', defaults={'description': 'Tests your basic Python knowledge', 'time_limit_minutes': 10}
        )
        if test.questions.count() == 0:
            q1 = Question.objects.create(test=test, text="Which keyword is used to define a function in Python?")
            Choice.objects.create(question=q1, text="function", is_correct=False)
            Choice.objects.create(question=q1, text="def", is_correct=True)
            Choice.objects.create(question=q1, text="func", is_correct=False)
            Choice.objects.create(question=q1, text="define", is_correct=False)

            q2 = Question.objects.create(test=test, text="Which data type is immutable in Python?")
            Choice.objects.create(question=q2, text="List", is_correct=False)
            Choice.objects.create(question=q2, text="Dictionary", is_correct=False)
            Choice.objects.create(question=q2, text="Tuple", is_correct=True)
            Choice.objects.create(question=q2, text="Set", is_correct=False)

    def create_testimonials(self):
        testimonials = [
            ('Ananya Sharma', 'CSE Student, DTU', 'This platform helped me figure out I actually wanted to go into data analysis, not just coding blindly.'),
            ('Rohit Verma', 'IT Student, NIT', 'The roadmap feature kept me on track for 3 months straight. Genuinely useful.'),
        ]
        for name, role, message in testimonials:
            Testimonial.objects.get_or_create(student_name=name, defaults={'role_or_college': role, 'message': message})

    def create_demo_staff_accounts(self):
        """
        Register only creates Students, so we create one demo Admin and one
        demo Counselor here for testing the admin/counselor panels.
        Change these passwords before actually deploying this project.
        """
        if not User.objects.filter(username='admin_demo').exists():
            admin_user = User.objects.create_user(
                username='admin_demo', password='Admin@12345', email='admin@example.com', first_name='Demo Admin'
            )
            Profile.objects.create(user=admin_user, role=Profile.ADMIN)
            self.stdout.write(self.style.SUCCESS("Demo admin created -> username: admin_demo / password: Admin@12345"))

        if not User.objects.filter(username='counselor_demo').exists():
            counselor_user = User.objects.create_user(
                username='counselor_demo', password='Counselor@12345', email='counselor@example.com',
                first_name='Demo Counselor'
            )
            Profile.objects.create(user=counselor_user, role=Profile.COUNSELOR)
            self.stdout.write(self.style.SUCCESS(
                "Demo counselor created -> username: counselor_demo / password: Counselor@12345"
            ))
