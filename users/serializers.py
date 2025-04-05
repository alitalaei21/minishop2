from rest_framework import serializers

from users.models import OtpRequest, User


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
class ObtainTokenSerializer(serializers.Serializer):
    token  = serializers.CharField(max_length=128,allow_null=False)
    refresh = serializers.CharField(max_length=128,allow_null=False)
    created = serializers.BooleanField()
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name','last_name','email']
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
    old_password = serializers.CharField(allow_null=False)
    new_password = serializers.CharField(allow_null=False)
    def validate_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("رمز اشتباه است")
        return value
    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(kwargs['new_password'])
        user.save()
        return user

