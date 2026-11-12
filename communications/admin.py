from django.contrib import admin
from .models import Unit, Profile, Message
@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ('name', 'kind', 'parent')
    list_filter = ('kind',)
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'unit')
    list_filter = ('role', 'unit')
@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'recipient', 'created_at')
    list_filter = ('created_at',)
    readonly_fields = ('sender', 'recipient', 'body', 'created_at', 'read_at')
    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return False

from .models import Bulletin, BulletinReceipt

@admin.register(Bulletin)
class BulletinAdmin(admin.ModelAdmin):
    list_display = ('title', 'sender', 'unit', 'priority', 'created_at')
    list_filter = ('unit', 'priority')
    readonly_fields = ('title', 'body', 'sender', 'unit', 'priority', 'created_at')
    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return False
    def has_delete_permission(self, request, obj=None): return False

@admin.register(BulletinReceipt)
class BulletinReceiptAdmin(admin.ModelAdmin):
    list_display = ('bulletin', 'recipient', 'read_at', 'confirmed_at')
    readonly_fields = ('bulletin', 'recipient', 'read_at', 'confirmed_at')
    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return False
    def has_delete_permission(self, request, obj=None): return False
