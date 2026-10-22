"""
Models for the core app. This is where most of the actual 'career roadmap'
logic lives: career paths, roadmaps, learning resources, skill tests,
notifications, resumes, and the home page content (testimonials, contact form).
"""
from django.db import models
from django.contrib.auth.models import User
from accounts.models import Profile


class CareerPath(models.Model):
    """
    A career option a student can be recommended, e.g. 'Python Developer'.
    Admin manages these from the Django admin panel.
    """
    name = models.CharField(max_length=150, unique=True)
    description = models.TextField()
    # comma separated skills used by the recommendation engine to match students
    required_skills = models.TextField(help_text="Comma separated, e.g. Python, Django, SQL")
    average_salary = models.CharField(max_length=100, blank=True)
    icon_class = models.CharField(max_length=50, blank=True, help_text="Optional CSS icon class")

    def __str__(self):
        return self.name

    def required_skills_list(self):
        return [s.strip().lower() for s in self.required_skills.split(',') if s.strip()]


class Roadmap(models.Model):
    """One roadmap belongs to one career path (Full Stack Dev -> its own roadmap)"""
    career = models.OneToOneField(CareerPath, on_delete=models.CASCADE, related_name='roadmap')
    estimated_duration_months = models.PositiveIntegerField(default=6)

    def __str__(self):
        return f"Roadmap for {self.career.name}"


class RoadmapStage(models.Model):
    """
    A stage inside a roadmap: Beginner / Intermediate / Advanced.
    Each stage has multiple milestones (RoadmapItem below).
    """
    BEGINNER = 'beginner'
    INTERMEDIATE = 'intermediate'
    ADVANCED = 'advanced'
    LEVEL_CHOICES = [
        (BEGINNER, 'Beginner'),
        (INTERMEDIATE, 'Intermediate'),
        (ADVANCED, 'Advanced'),
    ]

    roadmap = models.ForeignKey(Roadmap, on_delete=models.CASCADE, related_name='stages')
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.roadmap.career.name} - {self.level}"


class RoadmapItem(models.Model):
    """A single milestone/task inside a stage, e.g. 'Learn Python basics'"""
    stage = models.ForeignKey(RoadmapStage, on_delete=models.CASCADE, related_name='items')
    title = models.CharField(max_length=200)
    resource_link = models.URLField(blank=True, help_text="Optional link to a book/video/course")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title


class StudentRoadmapProgress(models.Model):
    """
    Tracks which roadmap items a student has completed.
    One row per student per roadmap item they've marked as done.
    """
    student = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='roadmap_progress')
    item = models.ForeignKey(RoadmapItem, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    completed_on = models.DateTimeField(blank=True, null=True)

    class Meta:
        unique_together = ('student', 'item')

    def __str__(self):
        return f"{self.student.user.username} - {self.item.title}"


class LearningResource(models.Model):
    """Books, docs, YouTube channels, practice sites shown in the Resources module"""
    BOOK = 'book'
    DOC = 'documentation'
    WEBSITE = 'practice_website'
    YOUTUBE = 'youtube'
    PLATFORM = 'coding_platform'
    TYPE_CHOICES = [
        (BOOK, 'Book'), (DOC, 'Documentation'), (WEBSITE, 'Practice Website'),
        (YOUTUBE, 'YouTube Channel'), (PLATFORM, 'Coding Platform'),
    ]

    title = models.CharField(max_length=200)
    resource_type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    link = models.URLField()
    category = models.CharField(max_length=100, help_text="e.g. Python, Web Development")
    description = models.TextField(blank=True)

    def __str__(self):
        return self.title


class Bookmark(models.Model):
    """A student saving a resource for later"""
    student = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='bookmarks')
    resource = models.ForeignKey(LearningResource, on_delete=models.CASCADE)
    saved_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'resource')


class SkillTest(models.Model):
    """A category of MCQ test, e.g. 'Programming Skills' or 'Logical Reasoning'"""
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    time_limit_minutes = models.PositiveIntegerField(default=15)

    def __str__(self):
        return self.title

    def total_marks(self):
        return self.questions.count()


class Question(models.Model):
    test = models.ForeignKey(SkillTest, on_delete=models.CASCADE, related_name='questions')
    text = models.CharField(max_length=500)

    def __str__(self):
        return self.text[:60]


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=250)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text


class TestAttempt(models.Model):
    """One attempt a student made at a skill test, with the score they got"""
    student = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='test_attempts')
    test = models.ForeignKey(SkillTest, on_delete=models.CASCADE)
    score = models.PositiveIntegerField(default=0)
    total = models.PositiveIntegerField(default=0)
    attempted_on = models.DateTimeField(auto_now_add=True)

    def percentage(self):
        return round((self.score / self.total) * 100, 1) if self.total else 0

    def __str__(self):
        return f"{self.student.user.username} - {self.test.title} - {self.score}/{self.total}"


class Resume(models.Model):
    """Keeps a history of every resume version a student has uploaded"""
    student = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='resumes')
    file = models.FileField(upload_to='resumes/')
    uploaded_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_on']

    def __str__(self):
        return f"Resume - {self.student.user.username} ({self.uploaded_on.date()})"


class Notification(models.Model):
    """
    A notification for a student. If student is left blank, it's treated as
    a broadcast announcement (shown to everyone) - used by Admin.
    """
    student = models.ForeignKey(Profile, on_delete=models.CASCADE, blank=True, null=True, related_name='notifications')
    message = models.CharField(max_length=300)
    created_on = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_on']

    def __str__(self):
        return self.message[:50]


class CounselorNote(models.Model):
    """A note/suggestion a counselor leaves on a student's profile"""
    counselor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notes_given')
    student = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='counselor_notes')
    note = models.TextField()
    assigned_career = models.ForeignKey(CareerPath, on_delete=models.SET_NULL, blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_on']

    def __str__(self):
        return f"Note for {self.student.user.username} by {self.counselor.username}"


class Testimonial(models.Model):
    """Shown on the home page, managed by admin"""
    student_name = models.CharField(max_length=100)
    role_or_college = models.CharField(max_length=150, blank=True)
    message = models.TextField()
    photo = models.ImageField(upload_to='testimonials/', blank=True, null=True)

    def __str__(self):
        return self.student_name


class ContactMessage(models.Model):
    """Messages submitted through the home page contact form"""
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200, blank=True)
    message = models.TextField()
    submitted_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.subject}"
