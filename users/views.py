from django.contrib.auth import get_user_model, authenticate
from django.core.serializers import serialize
from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken


from users import serializers
from users.models import OtpRequest
from users.serializers import ChangePasswordSerializer, SendSignupOtpSerializer, VerifyOtpSerializer


# Create your views here.
class OtpView(APIView):
    def post(self, request):
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

class LoginView(APIView):
    def post(self, request):
        serializer = serializers.VerifyOtpRequestSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            if OtpRequest.objects.is_valid(data['receiver'],data['password'],data['request_id']):
                return self.handle_login(data)
            else:
                return Response(status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def handle_login(self, otp):
        User = get_user_model()
        query = User.objects.filter(username=otp['receiver'])
        if query.exists():
            created = False
            user = query.first()
        else:
            user = User.objects.create(username=otp['receiver'],)
            created = True

        refresh = RefreshToken.for_user(user)

        from django.conf import settings
        import time
        from datetime import datetime

        current_time_ms = int(time.time() * 1000)
        access_token_seconds = int(settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds())
        refresh_token_seconds = int(settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds())

        access_token_expires_in_ms = current_time_ms + (access_token_seconds * 1000)
        refresh_token_expires_in_ms = current_time_ms + (refresh_token_seconds * 1000)

        # Set refresh token as HttpOnly cookie
        response_data = serializers.ObtainTokenSerializer({
            'token': str(refresh.access_token),
            'created': created,
            'access_token_expires_in': access_token_expires_in_ms,
            'refresh_token_expires_in': refresh_token_expires_in_ms,
            'user': user
        }).data

        # Set refresh token in cookie
        response = Response(response_data)
        response.set_cookie(
            key='refresh_token',
            value=str(refresh),
            httponly=True,
            samesite='Lax',
            secure=False,  # Set to True in production with HTTPS
            max_age=refresh_token_seconds  # Set to the actual refresh token lifetime
        )

        return response


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
        serializer = serializers.ChangePasswordSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "رمز عبور با موفقیت تغییر یافت"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SendOtpView(APIView):
    def post(self, request):
        serializer = SendSignupOtpSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'کد تأیید به ایمیل ارسال شد (در ترمینال قابل مشاهده است)'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyOtpView(APIView):
    def post(self, request):
        serializer = VerifyOtpSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.save()
            return Response({
                'access': data['access'],
                'refresh': data['refresh'],
                'user_created': data['user_created'],
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TokenRefreshView(APIView):
    """
    Takes a refresh token from cookie and returns a new access token
    """
    def post(self, request):
        serializer = serializers.TokenRefreshSerializer(data=request.data)
        if serializer.is_valid():
            refresh_token = request.COOKIES.get('refresh_token')

            if not refresh_token:
                return Response(
                    {"detail": "Refresh token not found in cookie"},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            try:
                refresh = RefreshToken(refresh_token)
                # Calculate expiration times in epoch milliseconds
                from django.conf import settings
                import time

                current_time_ms = int(time.time() * 1000)
                access_token_seconds = int(settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds())
                refresh_token_seconds = int(settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds())

                access_token_expires_in_ms = current_time_ms + (access_token_seconds * 1000)
                refresh_token_expires_in_ms = current_time_ms + (refresh_token_seconds * 1000)

                data = {
                    'token': str(refresh.access_token),
                    'access_token_expires_in': access_token_expires_in_ms,
                    'refresh_token_expires_in': refresh_token_expires_in_ms
                }

                return Response(data, status=status.HTTP_200_OK)
            except TokenError:
                return Response(
                    {"detail": "Invalid or expired token"},
                    status=status.HTTP_401_UNAUTHORIZED
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    """
    Logs out the user by invalidating refresh token and clearing cookie
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        response = Response({"detail": "Successfully logged out"}, status=status.HTTP_200_OK)

        # Delete the cookie containing the refresh token
        response.delete_cookie(
            key='refresh_token',
            samesite='Lax',
            secure=False #TODO: set to true in production with HTTPS
        )

        refresh_token = request.COOKIES.get('refresh_token')
        return response


class AuthStatusView(APIView):
    """
    Returns the authentication status and basic user info if authenticated
    """
    def get(self, request):
        if request.user.is_authenticated:
            # Return user data if authenticated
            serializer = serializers.ProfileSerializer(request.user)
            return Response({
                "isAuthenticated": True,
                "user": serializer.data
            }, status=status.HTTP_200_OK)
        else:
            # Return unauthenticated status
            return Response({
                "isAuthenticated": False
            }, status=status.HTTP_200_OK)
