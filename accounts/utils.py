from django.utils.translation import gettext as _

from accounts.models import VerificationCode
from sms import send_sms

def send_verification_sms(user=None):
    if user is not None:
        try:
            check_old_verification = VerificationCode.objects.filter(user=user)
            for u in check_old_verification:
                u.delete()
        except:
            pass
        # temp_verification_code = randint(1000,9999)
        temp_verification_code = 2222

        user_verification_code = VerificationCode()
        user_verification_code.user = user 
        user_verification_code.code = temp_verification_code
        user_verification_code.save()

        msg = _('Your verification code is ') + str(temp_verification_code)
        send_sms(
            msg,
            '+99365111111',
            user.phone_number,
            fail_silently=False,
        )