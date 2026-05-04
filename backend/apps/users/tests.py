import re

from django.core import mail
from django.test import override_settings
from rest_framework.test import APITestCase

from apps.users.models import User


@override_settings(
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    FRONTEND_URL='http://localhost:4200',
)
class PasswordResetTests(APITestCase):
    def test_password_reset_envia_email_y_permita_cambiar_password(self):
        user = User.objects.create_user(
            email='profesor@iespoligonosur.org',
            password='Temporal123',
            role=User.PROFESORADO,
        )

        request_response = self.client.post('/api/auth/password-reset/', {
            'email': user.email,
        }, format='json')

        self.assertEqual(request_response.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)

        match = re.search(r'uid=([^&\s]+)&token=([^\s]+)', mail.outbox[0].body)
        self.assertIsNotNone(match)
        uid, token = match.groups()

        confirm_response = self.client.post('/api/auth/password-reset/confirm/', {
            'uid': uid,
            'token': token,
            'nueva_password': 'NuevaPass123',
        }, format='json')

        self.assertEqual(confirm_response.status_code, 200)
        user.refresh_from_db()
        self.assertTrue(user.check_password('NuevaPass123'))
        self.assertFalse(user.must_change_password)
