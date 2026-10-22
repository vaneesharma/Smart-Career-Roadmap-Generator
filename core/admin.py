from django.contrib import admin
from .models import (
    CareerPath, Roadmap, RoadmapStage, RoadmapItem, StudentRoadmapProgress,
    LearningResource, Bookmark, SkillTest, Question, Choice, TestAttempt,
    Resume, Notification, CounselorNote, Testimonial, ContactMessage,
)


class RoadmapItemInline(admin.TabularInline):
    model = RoadmapItem
    extra = 1


class RoadmapStageInline(admin.TabularInline):
    model = RoadmapStage
    extra = 1


@admin.register(CareerPath)
class CareerPathAdmin(admin.ModelAdmin):
    list_display = ('name', 'average_salary')
    search_fields = ('name',)


@admin.register(Roadmap)
class RoadmapAdmin(admin.ModelAdmin):
    list_display = ('career', 'estimated_duration_months')
    inlines = [RoadmapStageInline]


@admin.register(RoadmapStage)
class RoadmapStageAdmin(admin.ModelAdmin):
    list_display = ('roadmap', 'level', 'order')
    inlines = [RoadmapItemInline]


@admin.register(LearningResource)
class LearningResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'resource_type', 'category')
    list_filter = ('resource_type', 'category')
    search_fields = ('title',)


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 4


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'test')
    inlines = [ChoiceInline]


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1
    show_change_link = True


@admin.register(SkillTest)
class SkillTestAdmin(admin.ModelAdmin):
    list_display = ('title', 'time_limit_minutes')
    inlines = [QuestionInline]


@admin.register(TestAttempt)
class TestAttemptAdmin(admin.ModelAdmin):
    list_display = ('student', 'test', 'score', 'total', 'attempted_on')
    list_filter = ('test',)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('message', 'student', 'created_on', 'is_read')


@admin.register(CounselorNote)
class CounselorNoteAdmin(admin.ModelAdmin):
    list_display = ('student', 'counselor', 'assigned_career', 'created_on')


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('student_name', 'role_or_college')


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'submitted_on')
    readonly_fields = ('submitted_on',)


admin.site.register(Bookmark)
admin.site.register(StudentRoadmapProgress)
admin.site.register(Resume)

admin.site.site_header = "Smart Career Roadmap Generator - Admin"
