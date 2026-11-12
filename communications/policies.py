"""Permisos para demostración académica. NO representan reglamentos militares reales."""
from .models import Profile

RANK = {
    Profile.DIRECTOR: 1, Profile.DEPUTY: 2, Profile.ACADEMIC: 3,
    Profile.BATTALION_COMMANDER: 4, Profile.COMMANDER: 5,
    Profile.CADRE: 6, Profile.SOLDIER: 7,
}


def within_unit(child_unit, ancestor_unit):
    """True cuando child_unit pertenece al subárbol de ancestor_unit."""
    seen = set()
    unit = child_unit
    while unit is not None and unit.pk not in seen:
        if unit.pk == ancestor_unit.pk:
            return True
        seen.add(unit.pk)
        unit = unit.parent
    return False


def can_message(sender, recipient):
    if not sender.is_authenticated or sender.pk == recipient.pk or not sender.is_active or not recipient.is_active:
        return False
    try:
        a, b = sender.profile, recipient.profile
    except (AttributeError, Profile.DoesNotExist):
        return False
    if a.role == Profile.DIRECTOR:
        return True
    # Respuestas ascendentes a la dirección, siempre disponibles en esta demo.
    if b.role == Profile.DIRECTOR:
        return True
    if a.role == Profile.DEPUTY:
        return True
    if b.role == Profile.DEPUTY:
        return True
    if a.role == Profile.ACADEMIC:
        return b.role != Profile.DIRECTOR and b.role != Profile.DEPUTY
    if b.role == Profile.ACADEMIC:
        return True
    # Mensajes entre mandos de batallón y sus subordinados, en ambos sentidos.
    if a.role == Profile.BATTALION_COMMANDER:
        return within_unit(b.unit, a.unit)
    if b.role == Profile.BATTALION_COMMANDER:
        return within_unit(a.unit, b.unit)
    # Entre compañías diferentes no hay acceso directo salvo jerarquías superiores.
    if a.unit_id != b.unit_id:
        return False
    if a.role == Profile.COMMANDER:
        return b.role in (Profile.CADRE, Profile.SOLDIER, Profile.COMMANDER)
    if a.role == Profile.CADRE:
        return b.role in (Profile.COMMANDER, Profile.CADRE, Profile.SOLDIER)
    if a.role == Profile.SOLDIER:
        return b.role in (Profile.COMMANDER, Profile.CADRE)
    return False
