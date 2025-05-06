from django.urls import path

from users.views import OtpView, LoginView, EmailSingupView, EmailLoginView, TokenRefreshView, LogoutView

urlpatterns = [
    path('singup', OtpView.as_view()),
    path('login', LoginView.as_view()),
    path('token/refresh', TokenRefreshView.as_view()),
    path('logout', LogoutView.as_view()),
    path('status', AuthStatusView.as_view()),
    path('singup',OtpView.as_view()),
    path('singupemail',EmailSingupView.as_view()),
    path('loginemail',EmailLoginView.as_view()),
]