from rest_framework import serializers
from rest_framework.views import APIView

from apps.core.account.models import TOTPUser
from apps.core.auths.serializers import MyTokenObtainPairSerializer
from apps.shared import mask_view, ResponseController, AuthMsg, BaseMsg


# 2fa
#  - POST       | Validate OTP for 2FA
#
# 2fa/integrate:
#  - GET        | All integrate status of user
#  - POST       | New integrate
#  - PUT        | Update status enable
#
# 2fa/integrate/{pk}
#  - GET        | Get integrate detail
#  - POST       | Valid integrate
#  - PUT        | Update integrate status
#  - DELETE     | Destroy integrate status


class TwoFA(APIView):
    @mask_view(login_require=True)
    def post(self, request, *args, **kwargs):
        otp = request.data.get('otp', None)
        ctx = {'otp': AuthMsg.OTP_NOT_MATCH}
        try:
            otp = int(otp)
        except ValueError:
            pass
        else:
            totp_objs = TOTPUser.objects.filter(user=request.user, confirmed=True)
            for obj in totp_objs:
                # auto increment throttling when verify is failure per TOTPUser
                # if allow many device, change from auto increment throttling to manual
                # if not TOTPUser will be locked out after a little time
                state, code = obj.verify(otp)
                if state is True:
                    result = {
                        'token': MyTokenObtainPairSerializer.get_full_token(user=request.user, is_verified=True),
                        **request.user.get_detail(),
                    }
                    return ResponseController.success_200(result, key_data='result')
                if code == 'LOCKED_OUT':
                    ctx = {'detail': AuthMsg.TWO_FA_LOCKED_OUT}
                elif code == 'OTP_USED':
                    ctx = {'detail': AuthMsg.OTP_BEEN_USED}
        raise serializers.ValidationError(ctx)


class TwoFAIntegrate(APIView):
    @mask_view(login_require=True)
    def get(self, request, *args, **kwargs):
        return ResponseController.success_200(
            data={
                'auth_2fa': request.user.auth_2fa,
                'auth_locked_out': request.user.auth_locked_out,
                'totp': TOTPUser.objects.filter(user=request.user, confirmed=True).exists()
            }
        )

    @mask_view(login_require=True)
    def post(self, request, *args, **kwargs):
        # generate OTP SECRET if is_integrate is False
        if request.user and request.user.is_authenticated is True and request.user.is_anonymous is False:
            totp_confirmed = TOTPUser.objects.filter(user=request.user, confirmed=True)
            if totp_confirmed.count() == 0:
                # clean all confirm is False
                obj_oldest = TOTPUser.objects.filter(user=request.user, confirmed=False)
                if obj_oldest:
                    obj_oldest.delete()

                # generate new TOTP
                obj_totp = TOTPUser(user=request.user)
                obj_totp.generate_secret_key()
                secret_key = obj_totp.get_secret_key()
                if secret_key:
                    obj_totp.save()
                    return ResponseController.success_200(
                        {
                            'id': str(obj_totp.id),
                            'qrcode': obj_totp.generate_otp_qri(),
                            'secret_key': secret_key,
                        }
                    )
                raise serializers.ValidationError(
                    {
                        'detail': AuthMsg.OTP_GENERATE_FAILURE
                    }
                )
            raise serializers.ValidationError(
                {
                    'detail': AuthMsg.OTP_INTEGRATED_BEFORE
                }
            )
        return ResponseController.unauthorized_401()

    @mask_view(login_require=True)
    def put(self, request, *args, **kwargs):
        is_enable = request.data.get('enabled', None)
        otp = request.data.get('otp', None)
        ctx = {'detail': AuthMsg.OTP_NOT_MATCH}
        if isinstance(is_enable, bool) and otp:
            totp_objs = TOTPUser.objects.filter(user=request.user, confirmed=True)
            for obj in totp_objs:
                state, code = obj.verify(otp)
                if state is True:
                    request.user.auth_2fa = is_enable
                    request.user.save(update_fields=['auth_2fa'])
                    return ResponseController.success_200(data={
                        'detail': BaseMsg.SUCCESSFULLY
                    })
                if code == 'LOCKED_OUT':
                    ctx = {'detail': AuthMsg.TWO_FA_LOCKED_OUT}
                elif code == 'OTP_USED':
                    ctx = {'detail': AuthMsg.OTP_BEEN_USED}
            raise serializers.ValidationError(ctx)
        errors = {}
        if not otp:
            errors['otp'] = BaseMsg.REQUIRED
        if not isinstance(is_enable, bool):
            errors['enabled'] = BaseMsg.REQUIRED
        raise serializers.ValidationError(errors)


class TwoFAIntegrateDetail(APIView):
    @mask_view(login_require=True)
    def put(self, request, *args, pk, **kwargs):
        try:
            obj = TOTPUser.objects.get(user=request.user, pk=pk)
            otp = int(request.data.get('otp', ''))
        except TOTPUser.DoesNotExist:
            return ResponseController.notfound_404()
        except ValueError:
            raise serializers.ValidationError(
                {
                    'otp': AuthMsg.OTP_NOT_MATCH
                }
            )
        else:
            ctx = {'otp': AuthMsg.OTP_NOT_MATCH}
            state, code = obj.verify(otp)
            if state:
                obj.set_confirmed(state=True, commit=True)
                return ResponseController.success_200(
                    data={
                        'detail': BaseMsg.SUCCESSFULLY
                    }
                )
            if code == 'LOCKED_OUT':
                ctx = {'detail': AuthMsg.TWO_FA_LOCKED_OUT}
            elif code == 'OTP_USED':
                ctx = {'detail': AuthMsg.OTP_BEEN_USED}
            raise serializers.ValidationError(ctx)

    # @mask_view(login_require=True)
    # def delete(self, request, *args, pk, **kwargs):
    #     return ResponseController.notfound_404()
