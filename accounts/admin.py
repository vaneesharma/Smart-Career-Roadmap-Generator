from django.contrib import admin
from .models import Profile, Certificate, ProjectEntry, Achievement


class CertificateInline(admin.TabularInline):
    model = Certificate
    extra = 0


class ProjectInline(admin.TabularInline):
    model = ProjectEntry
    extra = 0


class AchievementInline(admin.TabularInline):
    model = Achievement
    extra = 0


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'college', 'branch', 'cgpa', 'created_at')
    list_filter = ('role', 'branch')
    search_fields = ('user__username', 'user__email', 'college')
    inlines = [CertificateInline, ProjectInline, AchievementInline]
