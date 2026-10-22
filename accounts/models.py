"""
Models for the accounts app.
We don't touch Django's built-in User model directly (it already handles
username, password, email, login). Instead we create a Profile model that
sits next to it (one-to-one) and holds everything extra we need: role,
college info, skills, resume, etc.
"""
from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    # the three roles mentioned in the project requirements
    STUDENT = 'student'
    ADMIN = 'admin'
    COUNSELOR = 'counselor'

    ROLE_CHOICES = [
        (STUDENT, 'Student'),
        (ADMIN, 'Admin'),
        (COUNSELOR, 'Career Counselor'),
    ]

    # one-to-one means every Django User has exactly one Profile attached
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=STUDENT)

    # personal info
    phone = models.CharField(max_length=15, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    # education info (only really used when role == student)
    college = models.CharField(max_length=150, blank=True)
    branch = models.CharField(max_length=100, blank=True)
    semester = models.PositiveSmallIntegerField(blank=True, null=True)
    cgpa = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)

    # career related info, stored as comma separated text to keep things simple
    skills = models.TextField(blank=True, help_text="Comma separated, e.g. Python, HTML, SQL")
    interests = models.TextField(blank=True, help_text="Comma separated, e.g. Web Dev, AI")
    programming_languages = models.TextField(blank=True, help_text="Comma separated")
    career_goal = models.CharField(max_length=150, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} ({self.role})"

    def skills_list(self):
        """Turns the comma separated skills string into a clean python list"""
        return [s.strip() for s in self.skills.split(',') if s.strip()]

    def interests_list(self):
        return [i.strip() for i in self.interests.split(',') if i.strip()]

    def profile_completion_percent(self):
        """
        Rough calculation of how complete the profile is.
        We check a list of important fields, and see how many are filled in.
        Used on the dashboard as a progress bar.
        """
        fields_to_check = [
            self.phone, self.college, self.branch, self.semester,
            self.cgpa, self.skills, self.interests, self.career_goal,
        ]
        filled = sum(1 for f in fields_to_check if f)
        total = len(fields_to_check)
        picture_bonus = 1 if self.profile_picture else 0
        return int(((filled + picture_bonus) / (total + 1)) * 100)


class Certificate(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='certificates')
    title = models.CharField(max_length=200)
    issued_by = models.CharField(max_length=150, blank=True)
    issue_date = models.DateField(blank=True, null=True)
    certificate_file = models.FileField(upload_to='certificates/', blank=True, null=True)

    def __str__(self):
        return self.title


class ProjectEntry(models.Model):
    """Student's personal projects, shown on their profile"""
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='projects')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    tech_used = models.CharField(max_length=200, blank=True)
    project_link = models.URLField(blank=True)

    def __str__(self):
        return self.title


class Achievement(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='achievements')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    date_achieved = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.title
