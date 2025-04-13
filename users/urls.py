from django.urls import path

from users.views import OtpView, LoginView

urlpatterns = [
    path('singup',OtpView.as_view()),
    path('login',LoginView.as_view()),
]