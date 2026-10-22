"""
Forms for the accounts app.
Django forms handle both rendering the HTML input fields AND validating
whatever the user typed in, so we don't have to write that validation by hand.
"""
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile, Certificate, ProjectEntry, Achievement


class StudentRegisterForm(UserCreationForm):
    """
    Extends Django's built-in UserCreationForm (which already handles
    username + password + password confirmation + hashing) and adds
    email + full name on top of it.
    """
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=100, required=True, label="Full Name")

    class Meta:
        model = User
        fields = ['first_name', 'username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        if commit:
            user.save()
        return user


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            'profile_picture', 'phone', 'college', 'branch', 'semester',
            'cgpa', 'skills', 'interests', 'programming_languages', 'career_goal',
        ]
        widgets = {
            'skills': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Python, HTML, CSS, SQL'}),
            'interests': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Web Development, AI'}),
            'programming_languages': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Python, Java, C++'}),
        }


class UserBasicForm(forms.ModelForm):
    """Lets the user update first name / email alongside their Profile"""
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


class CertificateForm(forms.ModelForm):
    class Meta:
        model = Certificate
        fields = ['title', 'issued_by', 'issue_date', 'certificate_file']
        widgets = {'issue_date': forms.DateInput(attrs={'type': 'date'})}


class ProjectEntryForm(forms.ModelForm):
    class Meta:
        model = ProjectEntry
        fields = ['title', 'description', 'tech_used', 'project_link']


class AchievementForm(forms.ModelForm):
    class Meta:
        model = Achievement
        fields = ['title', 'description', 'date_achieved']
        widgets = {'date_achieved': forms.DateInput(attrs={'type': 'date'})}
