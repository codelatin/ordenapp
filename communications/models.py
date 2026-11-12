from django.conf import settings
from django.db import models

class Unit(models.Model):
    SCHOOL = 'school'
    BATTALION = 'battalion'
    COMPANY = 'company'
    DEPARTMENT = 'department'
    TYPES = [(SCHOOL, 'Escuela'), (BATTALION, 'Batallón'), (COMPANY, 'Compañía'), (DEPARTMENT, 'Dependencia')]
    name = models.CharField(max_length=100, unique=True)
    kind = models.CharField(max_length=20, choices=TYPES, default=COMPANY)
    parent = models.ForeignKey('self', on_delete=models.PROTECT, related_name='children', null=True, blank=True)

    def __str__(self):
        return self.name

class Profile(models.Model):
    DIRECTOR = 'director'
    DEPUTY = 'deputy'
    ACADEMIC = 'academic'
    BATTALION_COMMANDER = 'battalion'
    COMMANDER = 'commander'
    CADRE = 'cadre'
    SOLDIER = 'soldier'
    ROLES = [
        (DIRECTOR, 'Coronel director'),
        (DEPUTY, 'Coronel subdirector'),
        (ACADEMIC, 'Coronel vicerrector académico'),
        (BATTALION_COMMANDER, 'Teniente coronel comandante de batallón'),
        (COMMANDER, 'Comandante de compañía'),
        (CADRE, 'Cuadro de compañía'),
        (SOLDIER, 'Soldado bachiller'),
    ]
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLES)
    unit = models.ForeignKey(Unit, on_delete=models.PROTECT, related_name='members')
    def __str__(self): return f'{self.user.username} — {self.get_role_display()}'

class Message(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='sent_messages')
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='received_messages')
    body = models.TextField(max_length=2000)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    class Meta:
        ordering = ['created_at', 'id']
    def __str__(self): return f'{self.sender} → {self.recipient}: {self.body[:30]}'


class Bulletin(models.Model):
    NORMAL = 'normal'
    HIGH = 'high'
    PRIORITIES = [(NORMAL, 'Normal'), (HIGH, 'Alta')]
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='bulletins_sent')
    unit = models.ForeignKey(Unit, on_delete=models.PROTECT, null=True, blank=True, related_name='bulletins')
    title = models.CharField(max_length=160)
    body = models.TextField(max_length=4000)
    priority = models.CharField(max_length=10, choices=PRIORITIES, default=NORMAL)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at', '-pk']

    def __str__(self):
        return self.title


class BulletinReceipt(models.Model):
    bulletin = models.ForeignKey(Bulletin, on_delete=models.CASCADE, related_name='receipts')
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='bulletin_receipts')
    read_at = models.DateTimeField(null=True, blank=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['bulletin', 'recipient'], name='unique_bulletin_recipient')]

    def __str__(self):
        return f'{self.bulletin_id} — {self.recipient_id}'
