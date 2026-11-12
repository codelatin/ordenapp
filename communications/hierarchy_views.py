from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Profile, Unit
from .policies import can_message
from .bulletin_policies import available_units, can_publish
from django.contrib.auth import get_user_model

@login_required
def hierarchy(request):
    units = Unit.objects.select_related('parent').all().order_by('kind','name')
    users = get_user_model().objects.filter(is_active=True, profile__isnull=False).select_related('profile','profile__unit').order_by('profile__role','username')
    allowed_contact_ids = {u.pk for u in users if can_message(request.user,u)}
    return render(request, 'communications/hierarchy.html', {
        'units': units, 'members': users,
        'allowed_contact_ids': allowed_contact_ids,
        'my_publish_units': available_units(request.user),
        'can_publish': can_publish(request.user),
    })
