from django.urls import path

from users.views import OtpView, LoginView, TokenRefreshView, LogoutView, AuthStatusView, SendOtpView, VerifyOtpView

urlpatterns = [
    path('singup', OtpView.as_view()),
    path('login', LoginView.as_view()),
    path('token/refresh', TokenRefreshView.as_view()),
    path('logout', LogoutView.as_view()),
    path('status', AuthStatusView.as_view()),

    path('send-otp', SendOtpView.as_view()),
    path('verify-otp', VerifyOtpView.as_view()),

]