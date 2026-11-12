from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from communications.models import Unit, Profile

class Command(BaseCommand):
    help = 'Inicializa unidades y usuarios ficticios. No altera contraseñas existentes salvo --reset-passwords.'

    def add_arguments(self, parser):
        parser.add_argument('--reset-passwords', action='store_true', help='SOLO LOCAL: restablece contraseñas demo')

    @transaction.atomic
    def handle(self, *args, **options):
        school, _ = Unit.objects.update_or_create(name='EMSUB (demostración)', defaults={'kind': Unit.SCHOOL, 'parent': None})
        battalion, _ = Unit.objects.update_or_create(name='Batallón académico (ficticio)', defaults={'kind': Unit.BATTALION, 'parent': school})
        academic, _ = Unit.objects.update_or_create(name='Vicerrectoría académica (ficticia)', defaults={'kind': Unit.DEPARTMENT, 'parent': school})
        alfa, _ = Unit.objects.update_or_create(name='Compañía Alfa (ficticia)', defaults={'kind': Unit.COMPANY, 'parent': battalion})
        bravo, _ = Unit.objects.update_or_create(name='Compañía Bravo (ficticia)', defaults={'kind': Unit.COMPANY, 'parent': battalion})
        charlie, _ = Unit.objects.update_or_create(name='Compañía Charlie (ficticia)', defaults={'kind': Unit.COMPANY, 'parent': battalion})
        roster = [
            ('director', Profile.DIRECTOR, school),
            ('subdirector', Profile.DEPUTY, school),
            ('vicerrector', Profile.ACADEMIC, academic),
            ('batallon', Profile.BATTALION_COMMANDER, battalion),
            ('comandante', Profile.COMMANDER, alfa),
            ('cuadro', Profile.CADRE, alfa),
            ('soldado', Profile.SOLDIER, alfa),
            ('comandante_bravo', Profile.COMMANDER, bravo),
            ('soldado_bravo', Profile.SOLDIER, bravo),
            ('cuadro_charlie', Profile.CADRE, charlie),
            ('soldado_charlie', Profile.SOLDIER, charlie),
        ]
        User = get_user_model()
        for username, role, unit in roster:
            user, created = User.objects.get_or_create(username=username, defaults={'is_active': True})
            if created or options['reset_passwords']:
                user.set_password('DemoOrden2026!')
                user.save(update_fields=['password'])
            Profile.objects.update_or_create(user=user, defaults={'role': role, 'unit': unit})
            self.stdout.write(f'{username}: {"nuevo" if created else "existente"} / {role} / {unit.name}')
        self.stdout.write(self.style.SUCCESS('Demo lista. Contraseña de cuentas NUEVAS: DemoOrden2026!'))
        if not options['reset_passwords']:
            self.stdout.write('Las contraseñas de cuentas existentes NO se modificaron.')
