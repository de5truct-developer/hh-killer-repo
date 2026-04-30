from .models import Notification

def notifications(request):
    if request.user.is_authenticated:
        unread = Notification.objects.filter(user=request.user, is_read=False)
        return {
            'unread_notifications_count': unread.count(),
            'latest_notifications': unread[:5]
        }
    return {}
