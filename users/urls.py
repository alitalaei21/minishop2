from django.urls import path

from users.views import OtpView, LoginView, EmailSingupView, EmailLoginView

urlpatterns = [
    path('singup',OtpView.as_view()),
    path('login',LoginView.as_view()),
    path('singupemail',EmailSingupView.as_view()),
    path('loginemail',EmailLoginView.as_view()),
]