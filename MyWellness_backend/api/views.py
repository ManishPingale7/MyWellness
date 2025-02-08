from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from .serializers import UserSerializer
from django.contrib.auth import get_user_model
from .utils import calculate_bmi
import joblib
import os
from django.conf import settings
import pandas as pd


class PredictSleepDisorderView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    #     Required values:
    # [ STATIC - AGE,BMI_CODE,GENDER_CODE,OCCUPATION_CODE,
    # Sleep Duration,Quality of Sleep,Physical Activity Level,Heart Rate,Daily Steps,
    # systolic,diastolic]
    def get(self, request):

        # Get the data form + user DB
        bmi_cat = calculate_bmi(request.user.weight,request.user.height)[1]
        age = request.user.age
        gender = request.user.gender
        occupation = request.user.occupation

        #Retrive the data from the user watch set
        df=pd.read_csv(
            os.path.join(
                settings.BASE_DIR, "ML", "sleep_disorder.csv")
        )
        user_health_row = df.loc[2] #request.user.id]
        sleep_duration = user_health_row["Sleep Duration"]
        quality_of_sleep = user_health_row["Quality of Sleep"]
        physical_activity_level = user_health_row["Physical Activity Level"]
        heart_rate = user_health_row["Heart Rate"]
        daily_steps = user_health_row["Daily Steps"]
        systolic = user_health_row["systolic"]
        diastolic = user_health_row["diastolic"]

        print("Sleep Duration: ", type(sleep_duration),"\n\n",user_health_row)

        # Load the model
        model_path = os.path.join(
            settings.BASE_DIR, "ML", "model_pipeline.joblib")

        model = joblib.load(model_path)

        user_data_df = pd.DataFrame([[
            gender,
            age,
            occupation,
            sleep_duration,
            quality_of_sleep,
            physical_activity_level,
            bmi_cat,
            heart_rate,
            daily_steps,
            systolic,
            diastolic
        ]], columns=[
            'Gender',
            'Age',
            'Occupation',
            'Sleep Duration',
            'Quality of Sleep',
            'Physical Activity Level',
            'BMI Category',
            'Heart Rate',
            'Daily Steps',
            'systolic',
            'diastolic'
        ])
        
        prediction = model.predict(user_data_df)

        return Response({
            'success': True,
            "prediction":prediction,
            'message': 'Sleep disorder predicted successfully'
        }, status=status.HTTP_200_OK)


class SignupView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user_data = serializer.save()
            return Response({
                'sucess': True,
                'refresh': user_data['refresh'],
                'access': user_data['access'],
                'user_id': user_data['user_id']
            }, status=status.HTTP_201_CREATED)
        return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class SigninView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({'success': True, "message": "Logged in successfully"}, status=status.HTTP_200_OK)
