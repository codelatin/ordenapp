from .models import Profile, Unit
from .policies import within_unit

PUBLISHERS = (
    Profile.DIRECTOR, Profile.DEPUTY, Profile.ACADEMIC,
    Profile.BATTALION_COMMANDER, Profile.COMMANDER, Profile.CADRE,
)


def can_publish(user):
    try:
        return user.is_authenticated and user.is_active and user.profile.role in PUBLISHERS
    except (AttributeError, Profile.DoesNotExist):
        return False


def available_units(user):
    if not can_publish(user):
        return Unit.objects.none()
    profile = user.profile
    companies = Unit.objects.filter(kind=Unit.COMPANY).order_by('name')
    if profile.role in (Profile.DIRECTOR, Profile.DEPUTY, Profile.ACADEMIC):
        return companies
    if profile.role == Profile.BATTALION_COMMANDER:
        return [u for u in companies.select_related('parent', 'parent__parent') if within_unit(u, profile.unit)]
    return companies.filter(pk=profile.unit_id)
