from django.urls import path

from .views import SignupView, SigninView,chatbot,physical_activity_recommendation,sleep_recommendation, PredictSleepDisorderView


urlpatterns = [
    path('register/', SignupView.as_view(), name='signup'),
    path('signin/', SigninView.as_view(), name='signin'),
    path('chatbot/', chatbot, name='chatbot'),
    path('physical-activity-recommendation/', physical_activity_recommendation, name='physical_activity_recommendation'),
    path('sleep-recommendation/', sleep_recommendation, name='sleep_recommendation'),
    path('predict-sleep-disorder/', PredictSleepDisorderView.as_view(), name='predict-sleep-disorder'),

]
