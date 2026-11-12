from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils import timezone
from django.http import Http404
from django.shortcuts import render, get_object_or_404
from .models import Message
from .policies import can_message

@login_required
def inbox(request):
    users = [u for u in get_user_model().objects.filter(is_active=True).select_related('profile', 'profile__unit') if can_message(request.user, u) or can_message(u, request.user)]
    return render(request, 'communications/inbox.html', {'users': users})

@login_required
def chat(request, user_id):
    other = get_object_or_404(get_user_model(), pk=user_id, is_active=True)
    if not (can_message(request.user, other) or can_message(other, request.user)):
        raise Http404()
    Message.objects.filter(sender=other, recipient=request.user, read_at__isnull=True).update(read_at=timezone.now())
    messages = Message.objects.filter(Q(sender=request.user, recipient=other) | Q(sender=other, recipient=request.user)).select_related('sender')
    return render(request, 'communications/chat.html', {'other': other, 'chat_messages': messages})


@login_required
def dashboard(request):
    """Resumen privado del MVP; cada cifra pertenece al usuario autenticado."""
    person = request.user
    candidates = get_user_model().objects.filter(is_active=True).exclude(pk=person.pk).select_related('profile', 'profile__unit')
    contacts = [u for u in candidates if can_message(person, u) or can_message(u, person)]
    received = Message.objects.filter(recipient=person)
    sent = Message.objects.filter(sender=person)
    recent = Message.objects.filter(Q(sender=person) | Q(recipient=person)).select_related('sender', 'recipient').order_by('-created_at', '-pk')[:7]
    profile = getattr(person, 'profile', None)
    return render(request, 'communications/dashboard.html', {
        'contacts': contacts[:6],
        'contacts_count': len(contacts),
        'received_count': received.count(),
        'sent_count': sent.count(),
        'unread_count': received.filter(read_at__isnull=True).count(),
        'recent_messages': recent,
        'profile': profile,
    })
