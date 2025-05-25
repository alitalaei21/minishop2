from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import OtpRequest, User, EmailOtpRequest

User = get_user_model()

class RequestOtpSerializer(serializers.Serializer):
    receiver = serializers.CharField(max_length=100,allow_null=False)
    channel = serializers.ChoiceField(allow_null=False,choices=OtpRequest.OtpChannel.choices)
class OtpGetRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = OtpRequest
        fields = ['request_id',]
class VerifyOtpRequestSerializer(serializers.Serializer):
    receiver = serializers.CharField(max_length=100,allow_null=False)
    password = serializers.CharField(allow_null=False)
    request_id = serializers.UUIDField(allow_null=False)
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name','last_name','email']
class ObtainTokenSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=128,allow_null=False)
    created = serializers.BooleanField()
    access_token_expires_in = serializers.IntegerField()
    refresh_token_expires_in = serializers.IntegerField()
    user = ProfileSerializer(read_only=True)
class SetPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(allow_null=False)
    def validate_password(self, value):
        return value
    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(kwargs['password'])
        user.save()
        return user
class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for changing user password
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect")
        return value

    def validate(self, attrs):
        if attrs['old_password'] == attrs['new_password']:
            raise serializers.ValidationError({"new_password": "New password must be different from old password"})
        return attrs

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user

class TokenRefreshSerializer(serializers.Serializer):
    """
    Serializer for refreshing access token using refresh token from cookie
    """
    def validate(self, attrs):
        # The refresh token is obtained from the cookie, not from the request body
        return {}

class LogoutSerializer(serializers.Serializer):
    """
    Serializer for user logout - no fields required
    """
    pass


class SendSignupOtpSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(min_length=6)

    def create(self, validated_data):
        email = validated_data['email']
        code = EmailOtpRequest.generate_code()
        EmailOtpRequest.objects.create(email=email, code=code)

        print(f"[DEBUG] OTP for {email}: {code}")  # 👈 چاپ در ترمینال

        return validated_data





class VerifyOtpSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)
    password = serializers.CharField()

    def validate(self, data):
        email = data['email']
        code = data['code']

        try:
            otp = EmailOtpRequest.objects.filter(email=email, code=code).latest('created_at')
        except EmailOtpRequest.DoesNotExist:
            raise serializers.ValidationError("کد نادرست است")

        if not otp.is_valid():
            raise serializers.ValidationError("کد منقضی شده است")

        data['otp'] = otp
        return data

    def create(self, validated_data):
        email = validated_data['email']
        password = validated_data['password']

        user, created = User.objects.get_or_create(email=email, defaults={'username': email})
        user.set_password(password)
        user.save()

        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user_created': created
        }
