from django.urls import path
from .views import SignupView, SigninView, PredictSleepDisorderView

urlpatterns = [
    path('register/', SignupView.as_view(), name='signup'),
    path('signin/', SigninView.as_view(), name='signin'),
    path('predict-sleep-disorder/', PredictSleepDisorderView.as_view(), name='predict-sleep-disorder'),
]
