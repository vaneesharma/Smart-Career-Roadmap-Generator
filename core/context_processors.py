"""
A context processor runs on every single page request and adds extra
variables to the template automatically. We use this so the notification
bell icon in the navbar always knows the unread count, without every
view having to fetch it manually.
"""
from .models import Notification


def notifications_processor(request):
    if request.user.is_authenticated and hasattr(request.user, 'profile'):
        unread_count = Notification.objects.filter(
            student=request.user.profile, is_read=False
        ).count()
        return {'unread_notifications_count': unread_count}
    return {'unread_notifications_count': 0}
