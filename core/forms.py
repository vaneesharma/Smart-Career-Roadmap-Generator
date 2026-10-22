from django import forms
from .models import ContactMessage, Resume, CounselorNote


class CareerRecommendationForm(forms.Form):
    """
    The student doesn't have to retype skills here - we pre-fill from their
    profile, but we let them override interests/domain for this particular search.
    """
    skills = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 2}),
        help_text="Comma separated, e.g. Python, HTML, SQL", required=True
    )
    interests = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 2}),
        help_text="Comma separated, e.g. Web Development, AI", required=False
    )
    preferred_domain = forms.CharField(max_length=100, required=False)

    # these two are used by the AI roadmap generator shown below the match results
    EXPERIENCE_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    experience_level = forms.ChoiceField(choices=EXPERIENCE_CHOICES, initial='beginner', required=False)
    learning_goal = forms.CharField(
        max_length=200, required=False,
        widget=forms.TextInput(attrs={'placeholder': 'e.g. Get job ready in 6 months'})
    )


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message']


class ResumeUploadForm(forms.ModelForm):
    class Meta:
        model = Resume
        fields = ['file']


class CounselorNoteForm(forms.ModelForm):
    class Meta:
        model = CounselorNote
        fields = ['note', 'assigned_career']
