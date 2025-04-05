from rest_framework import serializers

from users.models import OtpRequest


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
