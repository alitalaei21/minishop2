from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import OtpRequest, User
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


class EmailSignupSerializer(serializers.Serializer):
    email = serializers.EmailField()
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("این ایمیل قبلاً ثبت شده است.")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user