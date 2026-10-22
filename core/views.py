"""
Views for the core app - this is the biggest file in the project because
it covers most of the actual features: home page, student dashboard,
career recommendation, roadmap tracking, learning resources, skill
assessment, resume, notifications, admin panel and counselor panel.
"""
import json

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Avg, Q
from django.http import HttpResponseForbidden, JsonResponse
from django.views.decorators.http import require_POST

from accounts.models import Profile
from .models import (
    CareerPath, Roadmap, RoadmapStage, RoadmapItem, StudentRoadmapProgress,
    LearningResource, Bookmark, SkillTest, Question, TestAttempt,
    Resume, Notification, CounselorNote, Testimonial, ContactMessage,
)
from .forms import CareerRecommendationForm, ContactForm, ResumeUploadForm, CounselorNoteForm
from .recommendation import recommend_careers
from .ai_roadmap import generate_ai_roadmap


# ---------------------------------------------------------------------------
# HOME PAGE
# ---------------------------------------------------------------------------
def home_view(request):
    """Public landing page - hero, features, testimonials, stats, contact form"""
    testimonials = Testimonial.objects.all()[:6]
    stats = {
        'students_count': Profile.objects.filter(role=Profile.STUDENT).count(),
        'careers_count': CareerPath.objects.count(),
        'resources_count': LearningResource.objects.count(),
        'tests_count': SkillTest.objects.count(),
    }

    if request.method == 'POST':
        contact_form = ContactForm(request.POST)
        if contact_form.is_valid():
            contact_form.save()
            messages.success(request, "Thanks for reaching out! We'll get back to you soon.")
            return redirect('core:home')
    else:
        contact_form = ContactForm()

    return render(request, 'core/home.html', {
        'testimonials': testimonials, 'stats': stats, 'contact_form': contact_form,
    })


# ---------------------------------------------------------------------------
# STUDENT DASHBOARD
# ---------------------------------------------------------------------------
def _role_required(user, role):
    return hasattr(user, 'profile') and user.profile.role == role


@login_required
def dashboard_view(request):
    profile = request.user.profile

    if profile.role == Profile.ADMIN:
        return redirect('core:admin_dashboard')
    if profile.role == Profile.COUNSELOR:
        return redirect('core:counselor_dashboard')

    recent_notifications = Notification.objects.filter(
        Q(student=profile) | Q(student__isnull=True)
    )[:5]

    latest_test = TestAttempt.objects.filter(student=profile).order_by('-attempted_on').first()
    total_roadmap_items = StudentRoadmapProgress.objects.filter(student=profile).count()
    completed_roadmap_items = StudentRoadmapProgress.objects.filter(student=profile, completed=True).count()
    roadmap_percent = int((completed_roadmap_items / total_roadmap_items) * 100) if total_roadmap_items else 0

    latest_resume = Resume.objects.filter(student=profile).first()

    context = {
        'profile': profile,
        'profile_completion': profile.profile_completion_percent(),
        'recent_notifications': recent_notifications,
        'latest_test': latest_test,
        'roadmap_percent': roadmap_percent,
        'latest_resume': latest_resume,
    }
    return render(request, 'core/dashboard.html', context)


# ---------------------------------------------------------------------------
# CAREER RECOMMENDATION
# ---------------------------------------------------------------------------
@login_required
def career_recommendation_view(request):
    profile = request.user.profile
    results = None

    if request.method == 'POST':
        form = CareerRecommendationForm(request.POST)
        if form.is_valid():
            skills = form.cleaned_data['skills'].split(',')
            interests = form.cleaned_data['interests'].split(',')
            domain = form.cleaned_data['preferred_domain']

            # keep the profile's skills up to date with whatever they entered here
            profile.skills = form.cleaned_data['skills']
            profile.interests = form.cleaned_data['interests']
            profile.save()

            results = recommend_careers(skills, interests, domain)
    else:
        # pre-fill the form using whatever is already saved on their profile
        form = CareerRecommendationForm(initial={
            'skills': profile.skills,
            'interests': profile.interests,
        })

    return render(request, 'core/career_recommendation.html', {'form': form, 'results': results})


# ---------------------------------------------------------------------------
# AI ROADMAP GENERATOR
# ---------------------------------------------------------------------------
@login_required
@require_POST
def ai_generate_roadmap_view(request):
    """
    Called through fetch() from the career recommendation page. Takes the
    career the student picked plus their skills/interests/level/goal, and
    returns a JSON roadmap. Tries the AI API first, and always falls back
    to a simple database driven roadmap so this endpoint never returns a
    server error to the frontend.
    """
    try:
        data = json.loads(request.body.decode('utf-8'))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({'error': 'Invalid request data.'}, status=400)

    career = (data.get('career') or '').strip()
    if not career:
        return JsonResponse({'error': 'Please choose a career first.'}, status=400)

    skills = [s.strip() for s in (data.get('skills') or '').split(',') if s.strip()]
    interests = [i.strip() for i in (data.get('interests') or '').split(',') if i.strip()]
    experience_level = data.get('experience_level') or 'beginner'
    learning_goal = (data.get('learning_goal') or '').strip()

    try:
        roadmap = generate_ai_roadmap(career, skills, interests, experience_level, learning_goal)
    except Exception:
        # last resort safety net - the page should never crash on this call
        return JsonResponse({'error': 'Could not generate a roadmap right now. Please try again.'}, status=500)

    return JsonResponse(roadmap)


# ---------------------------------------------------------------------------
# ROADMAP
# ---------------------------------------------------------------------------
@login_required
def roadmap_list_view(request):
    """Shows all careers, student picks one to view/track its roadmap"""
    careers = CareerPath.objects.filter(roadmap__isnull=False)
    return render(request, 'core/roadmap_list.html', {'careers': careers})


@login_required
def roadmap_detail_view(request, career_id):
    profile = request.user.profile
    career = get_object_or_404(CareerPath, id=career_id)
    roadmap = get_object_or_404(Roadmap, career=career)
    stages = roadmap.stages.prefetch_related('items')

    # figure out which items this student has already completed
    completed_ids = set(
        StudentRoadmapProgress.objects.filter(student=profile, completed=True)
        .values_list('item_id', flat=True)
    )

    total_items = sum(stage.items.count() for stage in stages)
    percent = int((len(completed_ids) / total_items) * 100) if total_items else 0

    return render(request, 'core/roadmap_detail.html', {
        'career': career, 'roadmap': roadmap, 'stages': stages,
        'completed_ids': completed_ids, 'percent': percent,
    })


@login_required
def toggle_roadmap_item_view(request, item_id):
    """Called when a student ticks/unticks a checkbox next to a roadmap milestone"""
    profile = request.user.profile
    item = get_object_or_404(RoadmapItem, id=item_id)
    progress, _ = StudentRoadmapProgress.objects.get_or_create(student=profile, item=item)
    progress.completed = not progress.completed
    progress.completed_on = timezone.now() if progress.completed else None
    progress.save()
    career_id = item.stage.roadmap.career_id
    return redirect('core:roadmap_detail', career_id=career_id)


# ---------------------------------------------------------------------------
# LEARNING RESOURCES
# ---------------------------------------------------------------------------
@login_required
def resources_view(request):
    profile = request.user.profile
    resources = LearningResource.objects.all()

    search_query = request.GET.get('q', '')
    category_filter = request.GET.get('category', '')

    if search_query:
        resources = resources.filter(title__icontains=search_query)
    if category_filter:
        resources = resources.filter(category__iexact=category_filter)

    bookmarked_ids = set(Bookmark.objects.filter(student=profile).values_list('resource_id', flat=True))
    categories = LearningResource.objects.values_list('category', flat=True).distinct()

    return render(request, 'core/resources.html', {
        'resources': resources, 'bookmarked_ids': bookmarked_ids,
        'categories': categories, 'search_query': search_query, 'category_filter': category_filter,
    })


@login_required
def toggle_bookmark_view(request, resource_id):
    profile = request.user.profile
    resource = get_object_or_404(LearningResource, id=resource_id)
    bookmark, created = Bookmark.objects.get_or_create(student=profile, resource=resource)
    if not created:
        bookmark.delete()
    return redirect('core:resources')


@login_required
def my_bookmarks_view(request):
    bookmarks = Bookmark.objects.filter(student=request.user.profile).select_related('resource')
    return render(request, 'core/my_bookmarks.html', {'bookmarks': bookmarks})


# ---------------------------------------------------------------------------
# SKILL ASSESSMENT
# ---------------------------------------------------------------------------
@login_required
def skill_test_list_view(request):
    tests = SkillTest.objects.all()
    return render(request, 'core/skill_test_list.html', {'tests': tests})


@login_required
def take_skill_test_view(request, test_id):
    profile = request.user.profile
    test = get_object_or_404(SkillTest, id=test_id)
    questions = test.questions.prefetch_related('choices')

    if request.method == 'POST':
        score = 0
        for question in questions:
            selected_choice_id = request.POST.get(f'question_{question.id}')
            if selected_choice_id:
                correct_choice = question.choices.filter(is_correct=True).first()
                if correct_choice and str(correct_choice.id) == selected_choice_id:
                    score += 1

        attempt = TestAttempt.objects.create(
            student=profile, test=test, score=score, total=questions.count()
        )
        return redirect('core:skill_test_result', attempt_id=attempt.id)

    return render(request, 'core/take_skill_test.html', {'test': test, 'questions': questions})


@login_required
def skill_test_result_view(request, attempt_id):
    attempt = get_object_or_404(TestAttempt, id=attempt_id, student=request.user.profile)
    return render(request, 'core/skill_test_result.html', {'attempt': attempt})


@login_required
def skill_test_history_view(request):
    attempts = TestAttempt.objects.filter(student=request.user.profile).select_related('test')
    return render(request, 'core/skill_test_history.html', {'attempts': attempts})


# ---------------------------------------------------------------------------
# RESUME
# ---------------------------------------------------------------------------
@login_required
def resume_view(request):
    profile = request.user.profile
    resumes = Resume.objects.filter(student=profile)

    if request.method == 'POST':
        form = ResumeUploadForm(request.POST, request.FILES)
        if form.is_valid():
            resume = form.save(commit=False)
            resume.student = profile
            resume.save()
            messages.success(request, "Resume uploaded successfully.")
            return redirect('core:resume')
    else:
        form = ResumeUploadForm()

    return render(request, 'core/resume.html', {'form': form, 'resumes': resumes})


# ---------------------------------------------------------------------------
# NOTIFICATIONS
# ---------------------------------------------------------------------------
@login_required
def notifications_view(request):
    profile = request.user.profile
    notifications = Notification.objects.filter(Q(student=profile) | Q(student__isnull=True))
    notifications.filter(student=profile, is_read=False).update(is_read=True)
    return render(request, 'core/notifications.html', {'notifications': notifications})


# ---------------------------------------------------------------------------
# ADMIN PANEL (custom, separate from Django's built-in /django-admin/)
# ---------------------------------------------------------------------------
@login_required
def admin_dashboard_view(request):
    if not _role_required(request.user, Profile.ADMIN):
        return HttpResponseForbidden("You don't have access to the admin panel.")

    context = {
        'total_students': Profile.objects.filter(role=Profile.STUDENT).count(),
        'total_counselors': Profile.objects.filter(role=Profile.COUNSELOR).count(),
        'total_careers': CareerPath.objects.count(),
        'total_resources': LearningResource.objects.count(),
        'total_tests': SkillTest.objects.count(),
        'recent_students': Profile.objects.filter(role=Profile.STUDENT).order_by('-created_at')[:8],
        'recent_messages': ContactMessage.objects.order_by('-submitted_on')[:5],
    }
    return render(request, 'admin_panel/dashboard.html', context)


@login_required
def admin_manage_students_view(request):
    if not _role_required(request.user, Profile.ADMIN):
        return HttpResponseForbidden("Access denied.")
    students = Profile.objects.filter(role=Profile.STUDENT).select_related('user')
    return render(request, 'admin_panel/manage_students.html', {'students': students})


@login_required
def admin_send_announcement_view(request):
    if not _role_required(request.user, Profile.ADMIN):
        return HttpResponseForbidden("Access denied.")
    if request.method == 'POST':
        message = request.POST.get('message', '').strip()
        if message:
            # student left blank on purpose -> this makes it a broadcast to everyone
            Notification.objects.create(student=None, message=message)
            messages.success(request, "Announcement sent to all students.")
    return redirect('core:admin_dashboard')


# ---------------------------------------------------------------------------
# COUNSELOR PANEL
# ---------------------------------------------------------------------------
@login_required
def counselor_dashboard_view(request):
    if not _role_required(request.user, Profile.COUNSELOR):
        return HttpResponseForbidden("You don't have access to the counselor panel.")
    students = Profile.objects.filter(role=Profile.STUDENT).select_related('user')
    return render(request, 'counselor_panel/dashboard.html', {'students': students})


@login_required
def counselor_student_detail_view(request, student_id):
    if not _role_required(request.user, Profile.COUNSELOR):
        return HttpResponseForbidden("Access denied.")

    student = get_object_or_404(Profile, id=student_id, role=Profile.STUDENT)
    notes = student.counselor_notes.select_related('counselor', 'assigned_career')
    test_attempts = student.test_attempts.select_related('test')

    if request.method == 'POST':
        form = CounselorNoteForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.student = student
            note.counselor = request.user
            note.save()
            messages.success(request, "Note added to student's profile.")
            return redirect('core:counselor_student_detail', student_id=student.id)
    else:
        form = CounselorNoteForm()

    return render(request, 'counselor_panel/student_detail.html', {
        'student': student, 'notes': notes, 'test_attempts': test_attempts, 'form': form,
    })
