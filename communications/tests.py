from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Bulletin, BulletinReceipt, Profile, Unit


class BulletinPermissionsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.alfa = Unit.objects.create(name='Alfa de prueba')
        cls.bravo = Unit.objects.create(name='Bravo de prueba')
        User = get_user_model()
        for name, role, unit in [
            ('jefe_alfa', Profile.COMMANDER, cls.alfa),
            ('jefe_bravo', Profile.COMMANDER, cls.bravo),
            ('soldado_alfa', Profile.SOLDIER, cls.alfa),
            ('soldado_bravo', Profile.SOLDIER, cls.bravo),
            ('director_demo', Profile.DIRECTOR, cls.alfa),
        ]:
            u = User.objects.create_user(username=name, password='PruebaSegura123!')
            Profile.objects.create(user=u, role=role, unit=unit)
            setattr(cls, name, u)

    def publish(self, unit, title='Aviso académico'):
        return self.client.post(reverse('bulletin_create'), {
            'unit': str(unit.pk), 'title': title, 'body': 'Reunión de prueba', 'priority': 'normal',
        })

    def test_commander_can_only_publish_to_own_unit(self):
        self.client.force_login(self.jefe_alfa)
        denied = self.publish(self.bravo)
        self.assertEqual(denied.status_code, 400)
        self.assertFalse(Bulletin.objects.exists())
        allowed = self.publish(self.alfa)
        self.assertEqual(allowed.status_code, 302)
        bulletin = Bulletin.objects.get()
        self.assertTrue(BulletinReceipt.objects.filter(bulletin=bulletin, recipient=self.soldado_alfa).exists())
        self.assertFalse(BulletinReceipt.objects.filter(bulletin=bulletin, recipient=self.soldado_bravo).exists())

    def test_soldier_cannot_publish(self):
        self.client.force_login(self.soldado_alfa)
        self.assertEqual(self.publish(self.alfa).status_code, 403)

    def test_non_recipient_cannot_read_or_confirm(self):
        self.client.force_login(self.jefe_alfa)
        self.publish(self.alfa)
        pk = Bulletin.objects.get().pk
        self.client.force_login(self.soldado_bravo)
        self.assertEqual(self.client.get(reverse('bulletin_detail', args=[pk])).status_code, 404)
        self.assertEqual(self.client.post(reverse('bulletin_confirm', args=[pk])).status_code, 404)

    def test_receipt_read_and_confirmation(self):
        self.client.force_login(self.jefe_alfa)
        self.publish(self.alfa)
        pk = Bulletin.objects.get().pk
        self.client.force_login(self.soldado_alfa)
        self.assertEqual(self.client.get(reverse('bulletin_detail', args=[pk])).status_code, 200)
        r = BulletinReceipt.objects.get(bulletin_id=pk, recipient=self.soldado_alfa)
        self.assertIsNotNone(r.read_at)
        self.assertIsNone(r.confirmed_at)
        self.assertEqual(self.client.post(reverse('bulletin_confirm', args=[pk])).status_code, 302)
        r.refresh_from_db()
        self.assertIsNotNone(r.confirmed_at)

    def test_director_can_publish_to_other_unit(self):
        self.client.force_login(self.director_demo)
        self.assertEqual(self.publish(self.bravo).status_code, 302)
        self.assertTrue(BulletinReceipt.objects.filter(recipient=self.soldado_bravo).exists())


from .policies import can_message
from .bulletin_policies import available_units

class HierarchyTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        school = Unit.objects.create(name='Escuela ficticia', kind=Unit.SCHOOL)
        battalion = Unit.objects.create(name='Batallón ficticio', kind=Unit.BATTALION, parent=school)
        cls.alfa = Unit.objects.create(name='Compañía A', kind=Unit.COMPANY, parent=battalion)
        cls.bravo = Unit.objects.create(name='Compañía B', kind=Unit.COMPANY, parent=battalion)
        User = get_user_model()
        for username, role, unit in [('dir_h', Profile.DIRECTOR,school),('bat_h', Profile.BATTALION_COMMANDER,battalion),('cmd_a',Profile.COMMANDER,cls.alfa),('cad_a',Profile.CADRE,cls.alfa),('sol_a',Profile.SOLDIER,cls.alfa),('cmd_b',Profile.COMMANDER,cls.bravo),('sol_b',Profile.SOLDIER,cls.bravo)]:
            u=User.objects.create_user(username=username,password='ClaveDemo2026!')
            Profile.objects.create(user=u,role=role,unit=unit)
            setattr(cls,username,u)

    def test_isolation_between_companies(self):
        self.assertFalse(can_message(self.cmd_a,self.sol_b))
        self.assertFalse(can_message(self.sol_a,self.cmd_b))
        self.assertTrue(can_message(self.sol_a,self.cmd_a))
        self.assertTrue(can_message(self.cad_a,self.sol_a))

    def test_battalion_scope(self):
        self.assertTrue(can_message(self.bat_h,self.sol_b))
        self.assertTrue(can_message(self.sol_a,self.bat_h))
        self.assertTrue(can_message(self.dir_h,self.sol_b))
        self.assertEqual({u.pk for u in available_units(self.cmd_a)},{self.alfa.pk})
        self.assertEqual({u.pk for u in available_units(self.bat_h)},{self.alfa.pk,self.bravo.pk})

    def test_soldier_cannot_publish_or_send_cross_company(self):
        self.client.force_login(self.sol_a)
        self.assertEqual(self.client.post(reverse('bulletin_create'), {'unit':self.alfa.pk,'title':'hola','body':'hola'}).status_code,403)
        self.assertEqual(self.client.get(reverse('chat',args=[self.sol_b.pk])).status_code,404)
        self.assertEqual(self.client.get(reverse('hierarchy')).status_code,200)


class BulletinTrackingTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.school = Unit.objects.create(name='Escuela pruebas seguimiento', kind=Unit.SCHOOL)
        cls.alpha = Unit.objects.create(name='Compañía pruebas seguimiento', kind=Unit.COMPANY, parent=cls.school)
        User = get_user_model()
        cls.sender = User.objects.create_user(username='seg_emisor', password='Prueba12345!')
        cls.reader = User.objects.create_user(username='seg_lector', password='Prueba12345!')
        cls.unread = User.objects.create_user(username='seg_pendiente', password='Prueba12345!')
        cls.outsider = User.objects.create_user(username='seg_ajeno', password='Prueba12345!')
        for user, role in ((cls.sender, Profile.COMMANDER), (cls.reader, Profile.SOLDIER), (cls.unread, Profile.SOLDIER), (cls.outsider, Profile.SOLDIER)):
            Profile.objects.create(user=user, role=role, unit=cls.alpha)
        cls.bulletin = Bulletin.objects.create(sender=cls.sender, unit=cls.alpha, title='Seguimiento demo', body='Mensaje de prueba')
        BulletinReceipt.objects.create(bulletin=cls.bulletin, recipient=cls.reader)
        BulletinReceipt.objects.create(bulletin=cls.bulletin, recipient=cls.unread)

    def test_only_sender_can_view_tracking_and_export(self):
        url = reverse('bulletin_tracking', args=[self.bulletin.pk])
        export = reverse('bulletin_tracking_csv', args=[self.bulletin.pk])
        self.assertEqual(self.client.get(url).status_code, 302)
        for user in (self.reader, self.outsider):
            self.client.force_login(user)
            self.assertEqual(self.client.get(url).status_code, 404)
            self.assertEqual(self.client.get(export).status_code, 404)
        self.client.force_login(self.sender)
        self.assertEqual(self.client.get(url).status_code, 200)
        self.assertEqual(self.client.get(export).status_code, 200)

    def test_tracking_counts_and_filters(self):
        self.client.force_login(self.reader)
        self.client.get(reverse('bulletin_detail', args=[self.bulletin.pk]))
        self.client.force_login(self.sender)
        url = reverse('bulletin_tracking', args=[self.bulletin.pk])
        response = self.client.get(url)
        self.assertEqual(response.context['counts']['total'], 2)
        self.assertEqual(response.context['counts']['pending'], 1)
        self.assertEqual(response.context['counts']['read_only'], 1)
        self.assertEqual(response.context['counts']['confirmed'], 0)
        self.assertEqual(self.client.get(url+'?estado=read').context['visible_count'], 1)
        self.assertEqual(self.client.get(url+'?estado=pending').context['visible_count'], 1)
        self.client.force_login(self.reader)
        self.client.post(reverse('bulletin_confirm', args=[self.bulletin.pk]))
        self.client.force_login(self.sender)
        updated = self.client.get(url)
        self.assertEqual(updated.context['counts']['confirmed'], 1)
        self.assertEqual(updated.context['counts']['read_only'], 0)
        self.assertEqual(updated.context['counts']['confirmed_percent'], 50)
        self.assertEqual(self.client.get(url+'?estado=confirmed').context['visible_count'], 1)

    def test_export_contains_only_recipients_of_this_bulletin(self):
        self.client.force_login(self.sender)
        response = self.client.get(reverse('bulletin_tracking_csv', args=[self.bulletin.pk]))
        decoded = response.content.decode('utf-8-sig')
        self.assertIn('seg_lector', decoded)
        self.assertIn('seg_pendiente', decoded)
        self.assertNotIn('seg_ajeno', decoded)


class NotificationSnapshotTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.unit = Unit.objects.create(name='Compañía para notificaciones')
        User = get_user_model()
        cls.sender = User.objects.create_user(username='emisor_n', password='Test12345!')
        cls.recipient = User.objects.create_user(username='receptor_n', password='Test12345!')
        cls.unrelated = User.objects.create_user(username='ajeno_n', password='Test12345!')
        Profile.objects.create(user=cls.sender, role=Profile.COMMANDER, unit=cls.unit)
        Profile.objects.create(user=cls.recipient, role=Profile.SOLDIER, unit=cls.unit)
        Profile.objects.create(user=cls.unrelated, role=Profile.SOLDIER, unit=cls.unit)
        cls.bulletin = Bulletin.objects.create(sender=cls.sender, unit=cls.unit, title='Aviso de ejemplo', body='Contenido simulado')
        cls.receipt = BulletinReceipt.objects.create(bulletin=cls.bulletin, recipient=cls.recipient)

    def test_login_required(self):
        response = self.client.get(reverse('notification_state'))
        self.assertEqual(response.status_code, 302)

    def test_snapshot_only_user_data(self):
        self.client.force_login(self.recipient)
        data = self.client.get(reverse('notification_state')).json()
        self.assertEqual(data['unread_bulletins'], 1)
        self.assertEqual(data['pending_confirmation'], 1)
        self.assertEqual(len(data['recent']), 1)
        self.assertEqual(data['recent'][0]['title'], 'Aviso de ejemplo')
        self.client.force_login(self.unrelated)
        other = self.client.get(reverse('notification_state')).json()
        self.assertEqual(other['unread_bulletins'], 0)
        self.assertEqual(other['recent'], [])

    def test_counts_change_after_read_and_confirm(self):
        self.client.force_login(self.recipient)
        self.client.get(reverse('bulletin_detail', args=[self.bulletin.pk]))
        data = self.client.get(reverse('notification_state')).json()
        self.assertEqual(data['unread_bulletins'], 0)
        self.assertEqual(data['pending_confirmation'], 1)
        self.client.post(reverse('bulletin_confirm', args=[self.bulletin.pk]))
        data = self.client.get(reverse('notification_state')).json()
        self.assertEqual(data['pending_confirmation'], 0)
        self.client.force_login(self.sender)
        sender_data = self.client.get(reverse('notification_state')).json()
        self.assertEqual(sender_data['recipient_confirmations_pending'], 0)
