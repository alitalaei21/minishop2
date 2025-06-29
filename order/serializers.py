from rest_framework import serializers

from order.models import Address


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'

    def validate(self, data):
        user = self.context['request'].user
        if user.addresses.count() >=3:
            raise serializers.ValidationError("شما نمی‌توانید بیش از 3 آدرس ثبت کنید.")
        return data
