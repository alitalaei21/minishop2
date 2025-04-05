from django.urls import path

from users.views import OtpView

urlpatterns = [
    path('',OtpView.as_view()),
]