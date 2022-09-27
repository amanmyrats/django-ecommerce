from django.test import TestCase

from accounts.models import Account, VerificationCode
from accounts.utils import send_verification_sms

class AccountsUtilsTest(TestCase):
    
    def setUp(self):
        self.user = Account.objects.create(
                            first_name='aman', last_name='aman', username='aman',
                            email='aman@aman.aman', phone_number='61111111'
                        )
    
    def test_send_verification_sms(self):
        vcode = VerificationCode()
        vcode.user = self.user
        vcode.code = 3333
        vcode.save()
        self.assertEqual(self.user.verificationcode.code, 3333)
        send_verification_sms(user=self.user)
        self.assertEqual(self.user.verificationcode.code, 2222)

