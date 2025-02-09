from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken
from .serializers import UserSerializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import UserSerializer
from rest_framework.decorators import api_view
from .utils import run_flow_physical,run_flow_chat,run_flow_sleep,calculate_bmi
import requests
import os
from dotenv import load_dotenv
load_dotenv()

from django.contrib.auth import get_user_model

import joblib
from django.conf import settings
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
import pandas as pd

# Define module-level variables for caching
MODEL = None
CSV_DF = None


def load_model():
    global MODEL
    if MODEL is None:
        model_path = os.path.join(
            settings.BASE_DIR, "ML", "model_pipeline.joblib")
        MODEL = joblib.load(model_path)
    return MODEL


def load_csv():
    global CSV_DF
    if CSV_DF is None:
        csv_path = os.path.join(settings.BASE_DIR, "ML", "sleep_disorder.csv")
        # Optionally, only load the required columns to speed up reading:
        CSV_DF = pd.read_csv(csv_path, usecols=[
            "Sleep Duration", "Quality of Sleep", "Physical Activity Level",
            "Heart Rate", "Daily Steps", "systolic", "diastolic"
        ]) 
    return CSV_DF


class PredictSleepDisorderView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    #     Required values:
    # [ STATIC - AGE,BMI_CODE,GENDER_CODE,OCCUPATION_CODE,
    # Sleep Duration,Quality of Sleep,Physical Activity Level,Heart Rate,Daily Steps,
    # systolic,diastolic]

    

    def get(self, request):
        try:
            # Retrieve user data from request.user
            bmi_cat = calculate_bmi(
                request.user.weight, request.user.height)[1]
            age = request.user.age
            gender = request.user.gender
            occupation = request.user.occupation

            # Retrieve health data from the cached CSV
            df = load_csv()
            try:
                user_health_row = df.loc[request.user.id]
            except KeyError:
                return Response({
                    'success': False,
                    'message': 'User health data not found in dataset.'
                }, status=status.HTTP_404_NOT_FOUND)

            sleep_duration = user_health_row["Sleep Duration"]
            quality_of_sleep = user_health_row["Quality of Sleep"]
            physical_activity_level = user_health_row["Physical Activity Level"]
            heart_rate = user_health_row["Heart Rate"]
            daily_steps = user_health_row["Daily Steps"]
            systolic = user_health_row["systolic"]
            diastolic = user_health_row["diastolic"]

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

            # Load the model from the cached version and predict
            model = load_model()
            prediction = model.predict(user_data_df)

            return Response({
                'success': True,
                'prediction': prediction[0],
                'message': 'Sleep disorder predicted successfully'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            # Log exception details in production (using Django logging, for instance)
            return Response({
                'success': False,
                'message': f'An error occurred during prediction: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

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
        user_health_row = df.loc[request.user.id] #request.user.id]
        sleep_duration = user_health_row["Sleep Duration"]
        quality_of_sleep = user_health_row["Quality of Sleep"]
        physical_activity_level = user_health_row["Physical Activity Level"]
        heart_rate = user_health_row["Heart Rate"]
        daily_steps = user_health_row["Daily Steps"]
        systolic = user_health_row["systolic"]
        diastolic = user_health_row["diastolic"]

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
            "prediction":prediction[0],
            'message': 'Sleep disorder predicted successfully'
        }, status=status.HTTP_200_OK)

 

class SignupView(APIView):
    def post(self, request):
        try:
            serializer = UserSerializer(data=request.data)
            if serializer.is_valid():
                user_data = serializer.save()
                return Response({
                    'success': True,
                    'access': user_data.get('access'),
                    'user_id': user_data.get('user_id')
                }, status=status.HTTP_201_CREATED)
            
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({

                'success': False,
                'error': 'An unexpected error occurred.',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SigninView(APIView):
    def post(self, request):
        try:
            username = request.data.get('username', '').strip()
            password = request.data.get('password', '').strip()

            if not username or not password:
                return Response(
                    {'error': 'Username and password are required.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            user = authenticate(username=username, password=password)
            if not user:
                return Response(
                    {'error': 'Invalid username or password.'},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            access_token = AccessToken.for_user(user)
            return Response(
                {'access': str(access_token), "success": True},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {'error': 'An unexpected error occurred.', 'details': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


    
@api_view(["POST"])
def chatbot(request):
    try:
        user_message = request.data.get("message", "").strip()
        if not user_message:
            return Response(
                {"error": "The 'message' field is required and cannot be empty."},
                status=status.HTTP_400_BAD_REQUEST
            )

        chatbot_response = run_flow_chat(user_message)
        if not chatbot_response:
            return Response(
                {"error": "No response generated from the chatbot. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        return Response({"response": chatbot_response}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response(
            {"error": "An unexpected error occurred.", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )





@api_view(["POST"])
def physical_activity_recommendation(request):
    try:
        user_message = request.data.get("message", "").strip()
        if not user_message:
            return Response(
                {"error": "The 'message' field is required and cannot be empty."},
                status=status.HTTP_400_BAD_REQUEST
            )

        recommendation = run_flow_physical(user_message)

        if not recommendation:
            return Response(
                {"error": "No recommendation could be generated. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response({"response": recommendation}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response(
            {"error": "An unexpected error occurred.", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )




@api_view(["POST"])
def sleep_recommendation(request):
    try:
        user_message = request.data.get("message", "").strip()
        
        if not user_message:
            return Response(
                {"error": "The 'message' field is required and cannot be empty."},
                status=status.HTTP_400_BAD_REQUEST
            )


        recommendation = run_flow_sleep(user_message)
        
        if not recommendation:
            return Response(
                {"error": "No recommendation could be generated. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response({"response": recommendation}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response(
            {"error": "An unexpected error occurred.", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

