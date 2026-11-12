from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Q, Count, F
from django.http import Http404, HttpResponseForbidden, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .bulletin_policies import available_units, can_publish
from .models import Bulletin, BulletinReceipt
import csv


def _send_progress(user_id, bulletin_id):
    layer = get_channel_layer()
    if layer is not None:
        async_to_sync(layer.group_send)(f'bulletins_user_{user_id}', {
            'type': 'bulletin.progress', 'bulletin_id': bulletin_id,
        })


def _notify_sender_of_progress(bulletin):
    _send_progress(bulletin.sender_id, bulletin.pk)


def _notify_recipient_of_progress(receipt):
    _send_progress(receipt.recipient_id, receipt.bulletin_id)


@login_required
def bulletin_list(request):
    received = BulletinReceipt.objects.filter(recipient=request.user).select_related('bulletin', 'bulletin__sender', 'bulletin__unit')
    published = Bulletin.objects.filter(sender=request.user).annotate(recipient_count=Count('receipts', distinct=True))
    return render(request, 'communications/bulletin_list.html', {
        'received': received.order_by('-bulletin__created_at'),
        'published': published,
        'unread_bulletins': received.filter(read_at__isnull=True).count(),
        'can_publish': can_publish(request.user),
    })


@login_required
def bulletin_create(request):
    if not can_publish(request.user):
        return HttpResponseForbidden('No puedes publicar comunicados.')
    units = available_units(request.user)
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        body = request.POST.get('body', '').strip()
        priority = request.POST.get('priority', Bulletin.NORMAL)
        unit_id = request.POST.get('unit')
        unit = next((u for u in units if str(u.pk) == str(unit_id)), None) if unit_id and unit_id.isdigit() else None
        errors = []
        if unit is None:
            errors.append('Selecciona una unidad autorizada.')
        if not (1 <= len(title) <= 160):
            errors.append('El título debe tener entre 1 y 160 caracteres.')
        if not (1 <= len(body) <= 4000):
            errors.append('El mensaje debe tener entre 1 y 4000 caracteres.')
        if priority not in (Bulletin.NORMAL, Bulletin.HIGH):
            errors.append('La prioridad no es válida.')
        if not errors:
            User = get_user_model()
            recipients = list(User.objects.filter(is_active=True, profile__unit=unit).exclude(pk=request.user.pk).values_list('pk', flat=True))
            if not recipients:
                errors.append('Esta unidad todavía no tiene destinatarios activos.')
        if not errors:
            with transaction.atomic():
                bulletin = Bulletin.objects.create(sender=request.user, unit=unit, title=title, body=body, priority=priority)
                BulletinReceipt.objects.bulk_create([BulletinReceipt(bulletin=bulletin, recipient_id=pk) for pk in recipients])
                def notify():
                    layer = get_channel_layer()
                    for pk in recipients:
                        async_to_sync(layer.group_send)(f'bulletins_user_{pk}', {
                            'type': 'bulletin.notice',
                            'bulletin': {'id': bulletin.pk, 'title': bulletin.title, 'priority': bulletin.priority, 'sender': request.user.username},
                        })
                transaction.on_commit(notify)
            messages.success(request, f'Comunicado enviado a {len(recipients)} destinatarios.')
            return redirect('bulletin_detail', pk=bulletin.pk)
        return render(request, 'communications/bulletin_form.html', {
            'units': units, 'errors': errors, 'values': request.POST,
        }, status=400)
    return render(request, 'communications/bulletin_form.html', {'units': units})


@login_required
def bulletin_detail(request, pk):
    bulletin = get_object_or_404(Bulletin.objects.select_related('sender', 'unit'), pk=pk)
    is_sender = bulletin.sender_id == request.user.pk
    receipt = BulletinReceipt.objects.filter(bulletin=bulletin, recipient=request.user).first()
    if not is_sender and not receipt:
        raise Http404()
    if receipt and receipt.read_at is None:
        BulletinReceipt.objects.filter(pk=receipt.pk, read_at__isnull=True).update(read_at=timezone.now())
        receipt.refresh_from_db()
        _notify_sender_of_progress(bulletin)
    receipts = None  # La vista de seguimiento separada requiere ser el emisor.
    return render(request, 'communications/bulletin_detail.html', {
        'bulletin': bulletin, 'receipt': receipt, 'receipts': receipts, 'is_sender': is_sender,
    })


@require_POST
@login_required
def bulletin_confirm(request, pk):
    receipt = get_object_or_404(BulletinReceipt, bulletin_id=pk, recipient=request.user)
    if receipt.confirmed_at is None:
        receipt.confirmed_at = timezone.now()
        if receipt.read_at is None:
            receipt.read_at = receipt.confirmed_at
        receipt.save(update_fields=['read_at', 'confirmed_at'])
        _notify_sender_of_progress(receipt.bulletin)
        _notify_recipient_of_progress(receipt)
    messages.success(request, 'Recepción confirmada.')
    return redirect('bulletin_detail', pk=pk)


# Seguimiento de comunicados. El conjunto de destinatarios ya se congela al publicar.
# No usamos permisos basados solo en el cargo: únicamente el emisor puede consultar
# el listado individual, evitando filtrar la identidad de otras compañías.

VALID_TRACKING_STATES = ('all', 'pending', 'read', 'confirmed')


def _sender_bulletin_or_404(user, pk):
    return get_object_or_404(
        Bulletin.objects.select_related('sender', 'unit'),
        pk=pk, sender=user,
    )


def _tracking_counts(bulletin):
    return bulletin.receipts.aggregate(
        total=Count('id'),
        confirmed=Count('id', filter=Q(confirmed_at__isnull=False)),
        read_total=Count('id', filter=Q(read_at__isnull=False)),
        pending=Count('id', filter=Q(read_at__isnull=True, confirmed_at__isnull=True)),
    )


def _filter_tracking_receipts(bulletin, state):
    qs = bulletin.receipts.select_related('recipient', 'recipient__profile', 'recipient__profile__unit').order_by('recipient__username')
    if state == 'pending':
        return qs.filter(read_at__isnull=True, confirmed_at__isnull=True)
    if state == 'read':
        return qs.filter(read_at__isnull=False, confirmed_at__isnull=True)
    if state == 'confirmed':
        return qs.filter(confirmed_at__isnull=False)
    return qs


@login_required
def bulletin_tracking(request, pk):
    bulletin = _sender_bulletin_or_404(request.user, pk)
    state = request.GET.get('estado', 'all')
    if state not in VALID_TRACKING_STATES:
        state = 'all'
    counts = _tracking_counts(bulletin)
    total = counts['total'] or 0
    counts['read_only'] = (counts['read_total'] or 0) - (counts['confirmed'] or 0)
    counts['confirmed_percent'] = round((counts['confirmed'] or 0) * 100 / total) if total else 0
    counts['read_percent'] = round((counts['read_total'] or 0) * 100 / total) if total else 0
    receipts = _filter_tracking_receipts(bulletin, state)
    return render(request, 'communications/bulletin_tracking.html', {
        'bulletin': bulletin, 'counts': counts, 'receipts': receipts,
        'state': state, 'visible_count': receipts.count(),
    })


@login_required
def bulletin_tracking_csv(request, pk):
    bulletin = _sender_bulletin_or_404(request.user, pk)
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="ordenapp_comunicado_{bulletin.pk}_seguimiento.csv"'
    # BOM para que Excel en Windows reconozca los acentos.
    response.write('\ufeff')
    writer = csv.writer(response)
    writer.writerow(['Comunicado', 'Unidad destinataria', 'Usuario', 'Cargo', 'Unidad de usuario', 'Estado', 'Lectura', 'Confirmación'])
    for receipt in _filter_tracking_receipts(bulletin, 'all').iterator():
        if receipt.confirmed_at:
            state = 'Confirmado'
        elif receipt.read_at:
            state = 'Leído - sin confirmar'
        else:
            state = 'Pendiente de lectura'
        profile = getattr(receipt.recipient, 'profile', None)
        writer.writerow([
            bulletin.title, bulletin.unit.name if bulletin.unit_id else '',
            receipt.recipient.username,
            profile.get_role_display() if profile else '',
            profile.unit.name if profile and profile.unit_id else '',
            state,
            timezone.localtime(receipt.read_at).strftime('%d/%m/%Y %H:%M') if receipt.read_at else '',
            timezone.localtime(receipt.confirmed_at).strftime('%d/%m/%Y %H:%M') if receipt.confirmed_at else '',
        ])
    return response
