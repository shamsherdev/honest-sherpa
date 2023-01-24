from superadmin.models import*

def notify(request):
    notification = Notification.objects.filter(sender_id = request.user.id)
    return notification