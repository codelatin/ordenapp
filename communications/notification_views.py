from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Count, Q
from django.urls import reverse
from .models import Bulletin, BulletinReceipt


@login_required
def notification_state(request):
    """Sólo comunica datos pertenecientes al usuario autenticado."""
    user = request.user
    receipts = BulletinReceipt.objects.filter(recipient=user)
    new_count = receipts.filter(read_at__isnull=True).count()
    awaiting_confirmation = receipts.filter(confirmed_at__isnull=True).count()
    recent_receipts = list(receipts.select_related('bulletin', 'bulletin__sender').order_by('-bulletin__created_at', '-pk')[:6])
    recent = [{
        'id': r.bulletin_id,
        'title': r.bulletin.title,
        'sender': r.bulletin.sender.username,
        'priority': r.bulletin.priority,
        'read': r.read_at is not None,
        'confirmed': r.confirmed_at is not None,
        'url': reverse('bulletin_detail', args=[r.bulletin_id]),
    } for r in recent_receipts]
    sent = Bulletin.objects.filter(sender=user)
    sent_total = sent.count()
    recipient_stats = BulletinReceipt.objects.filter(bulletin__sender=user).aggregate(
        total=Count('id'),
        confirmed=Count('id', filter=Q(confirmed_at__isnull=False)),
    )
    awaiting_from_recipients = (recipient_stats['total'] or 0) - (recipient_stats['confirmed'] or 0)
    return JsonResponse({
        'unread_bulletins': new_count,
        'pending_confirmation': awaiting_confirmation,
        'recent': recent,
        'published_count': sent_total,
        'recipient_confirmations_pending': awaiting_from_recipients,
    })
