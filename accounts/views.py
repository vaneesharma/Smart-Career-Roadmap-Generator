"""
Views for the accounts app. A 'view' in Django is just a python function
that takes a web request and returns a web response (usually rendered HTML).
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import (
    PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView,
    PasswordResetCompleteView, LoginView,
)
from django.contrib import messages
from django.urls import reverse_lazy

from .forms import (
    StudentRegisterForm, ProfileEditForm, UserBasicForm,
    CertificateForm, ProjectEntryForm, AchievementForm,
)
from .models import Profile


def register_view(request):
    """Handles new student sign up. Every new user automatically becomes role=student"""
    if request.user.is_authenticated:
        return redirect('core:dashboard')

    if request.method == 'POST':
        form = StudentRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # every new signup gets a Profile row with role=student by default
            Profile.objects.create(user=user, role=Profile.STUDENT)
            login(request, user)
            messages.success(request, "Account created successfully. Welcome aboard!")
            return redirect('core:dashboard')
    else:
        form = StudentRegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


class RoleBasedLoginView(LoginView):
    """
    Custom login view so we can send Admin / Counselor / Student to different
    dashboards after they log in, instead of always going to the same page.
    """
    template_name = 'accounts/login.html'

    def get_success_url(self):
        user = self.request.user
        try:
            role = user.profile.role
        except Profile.DoesNotExist:
            return reverse_lazy('core:dashboard')

        if role == Profile.ADMIN:
            return reverse_lazy('core:admin_dashboard')
        elif role == Profile.COUNSELOR:
            return reverse_lazy('core:counselor_dashboard')
        return reverse_lazy('core:dashboard')


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('core:home')


@login_required
def edit_profile_view(request):
    """Lets a logged in user update their profile info + profile picture"""
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        user_form = UserBasicForm(request.POST, instance=request.user)
        profile_form = ProfileEditForm(request.POST, request.FILES, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('accounts:edit_profile')
    else:
        user_form = UserBasicForm(instance=request.user)
        profile_form = ProfileEditForm(instance=profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'certificate_form': CertificateForm(),
        'project_form': ProjectEntryForm(),
        'achievement_form': AchievementForm(),
        'profile': profile,
    }
    return render(request, 'accounts/edit_profile.html', context)


@login_required
def add_certificate_view(request):
    if request.method == 'POST':
        form = CertificateForm(request.POST, request.FILES)
        if form.is_valid():
            cert = form.save(commit=False)
            cert.profile = request.user.profile
            cert.save()
            messages.success(request, "Certificate added.")
    return redirect('accounts:edit_profile')


@login_required
def add_project_view(request):
    if request.method == 'POST':
        form = ProjectEntryForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.profile = request.user.profile
            project.save()
            messages.success(request, "Project added.")
    return redirect('accounts:edit_profile')


@login_required
def add_achievement_view(request):
    if request.method == 'POST':
        form = AchievementForm(request.POST)
        if form.is_valid():
            achievement = form.save(commit=False)
            achievement.profile = request.user.profile
            achievement.save()
            messages.success(request, "Achievement added.")
    return redirect('accounts:edit_profile')


# ---------------- Password reset flow (uses Django's built-in views) ----------------
# We just point them to our own templates so they match our site's theme.

class CustomPasswordResetView(PasswordResetView):
    template_name = 'accounts/password_reset.html'
    email_template_name = 'accounts/password_reset_email.html'
    success_url = reverse_lazy('accounts:password_reset_done')


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'accounts/password_reset_done.html'


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'accounts/password_reset_confirm.html'
    success_url = reverse_lazy('accounts:password_reset_complete')


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'accounts/password_reset_complete.html'
