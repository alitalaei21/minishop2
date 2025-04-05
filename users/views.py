from django.contrib.auth import get_user_model
from django.core.serializers import serialize
from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from users import serializers
from users.models import OtpRequest


# Create your views here.
class OtpView(APIView):
    def get(self, request):
        serializer = serializers.RequestOtpSerializer(data=request.query_params)
        if serializer.is_valid():
            data = serializer.validated_data
            try:
                otp = OtpRequest.objects.generate(data)
                return Response(data=serializers.OtpGetRequestSerializer(otp).data, status=status.HTTP_200_OK)
            except Exception as e:
                print(e)
                return Response( status=status.HTTP_500_INTERNAL_SERVER_ERROR,data=serializer.errors)
        else:
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def post(self, request):
        serializer = serializers.VerifyOtpRequestSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            if OtpRequest.objects.is_valid(data['receiver'],data['password'],data['request_id']):
                return Response(self.handel_login(data))
            else:
                return Response(status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def handel_login(self,otp):
        User = get_user_model()
        query = User.objects.filter(username=otp['receiver'])
        if query.exists():
            created = False
            user = query.first()
        else:
            user = User.objects.create(username=otp['receiver'],)
            created = True
        refresh = RefreshToken.for_user(user)
        return serializers.ObtainTokenSerializer({
            'refresh': str(refresh),
            'token': str(refresh.access_token),
            'created':created

        }).data


class ProfileUpdate(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = serializers.ProfileSerializer(data=request.data)
        return Response(serializer.data)

    def put(self, request):
        serializer = serializers.ProfileSerializer(instance=request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SetPasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = serializers.SetPasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "رمز عبور با موفقیت تغییر یافت"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
