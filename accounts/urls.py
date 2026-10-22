"""
URL routes for the accounts app. All of these sit under /accounts/ because
that's the prefix we gave it in the root urls.py
"""
from django.urls import path
from django.contrib.auth.views import LogoutView, PasswordChangeView, PasswordChangeDoneView
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.RoleBasedLoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('profile/edit/', views.edit_profile_view, name='edit_profile'),
    path('profile/add-certificate/', views.add_certificate_view, name='add_certificate'),
    path('profile/add-project/', views.add_project_view, name='add_project'),
    path('profile/add-achievement/', views.add_achievement_view, name='add_achievement'),

    # change password (user already logged in and knows current password)
    path('password-change/', PasswordChangeView.as_view(
        template_name='accounts/password_change.html'), name='password_change'),
    path('password-change/done/', PasswordChangeDoneView.as_view(
        template_name='accounts/password_change_done.html'), name='password_change_done'),

    # forgot password (user is logged out, resets via email link)
    path('password-reset/', views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', views.CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', views.CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
