"""URL routes for the core app - these all sit at the root of the site (no prefix)"""
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('dashboard/', views.dashboard_view, name='dashboard'),

    # career recommendation
    path('career/recommend/', views.career_recommendation_view, name='career_recommendation'),
    path('career/ai-roadmap/', views.ai_generate_roadmap_view, name='ai_generate_roadmap'),

    # roadmap
    path('roadmap/', views.roadmap_list_view, name='roadmap_list'),
    path('roadmap/<int:career_id>/', views.roadmap_detail_view, name='roadmap_detail'),
    path('roadmap/item/<int:item_id>/toggle/', views.toggle_roadmap_item_view, name='toggle_roadmap_item'),

    # learning resources
    path('resources/', views.resources_view, name='resources'),
    path('resources/<int:resource_id>/bookmark/', views.toggle_bookmark_view, name='toggle_bookmark'),
    path('resources/my-bookmarks/', views.my_bookmarks_view, name='my_bookmarks'),

    # skill assessment
    path('assessment/', views.skill_test_list_view, name='skill_test_list'),
    path('assessment/<int:test_id>/take/', views.take_skill_test_view, name='take_skill_test'),
    path('assessment/result/<int:attempt_id>/', views.skill_test_result_view, name='skill_test_result'),
    path('assessment/history/', views.skill_test_history_view, name='skill_test_history'),

    # resume
    path('resume/', views.resume_view, name='resume'),

    # notifications
    path('notifications/', views.notifications_view, name='notifications'),

    # admin panel (custom)
    path('management/dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
    path('management/students/', views.admin_manage_students_view, name='admin_manage_students'),
    path('management/announcement/', views.admin_send_announcement_view, name='admin_send_announcement'),

    # counselor panel
    path('counselor/dashboard/', views.counselor_dashboard_view, name='counselor_dashboard'),
    path('counselor/student/<int:student_id>/', views.counselor_student_detail_view, name='counselor_student_detail'),
]
