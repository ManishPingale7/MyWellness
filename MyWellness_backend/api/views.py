import logging
from datetime import datetime, timedelta
from datetime import datetime
from .serializers import ActivityDataSerializer 
from .models import ActivityData
from rest_framework.decorators import api_view, authentication_classes, permission_classes
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

logger = logging.getLogger(__name__)
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
            print(user_data_df)
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


@api_view(["GET"])
@authentication_classes([JWTAuthentication])  # JWT Authentication
@permission_classes([IsAuthenticated])  # Ensure the user is authenticated
def day_activity(request,date):
    try:
        if not date:
            return Response(
                {"error": "The 'date' query parameter is required and cannot be empty."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            date = datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            return Response(
                {"error": "Invalid date format. Please use 'YYYY-MM-DD'."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user_id = request.user.id
        if user_id is None:
            return Response({'error': 'You are not authorized to access this data'}, status=status.HTTP_403_FORBIDDEN)

        try:
            activity = ActivityData.objects.get(
                user_id=user_id, activity_date=date)
        except ActivityData.DoesNotExist:
            return Response(
                {"error": "No data found for the specified user and date."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ActivityDataSerializer(activity)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response(
            {"error": "An unexpected error occurred.", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["GET"])
@authentication_classes([JWTAuthentication])  
@permission_classes([IsAuthenticated])  
def week_activity(request):
    start_date_str = request.query_params.get("start_date", "").strip()
    end_date_str = request.query_params.get("end_date", "").strip()

    # Check params
    if not start_date_str or not end_date_str:
        return Response(
            {"error": "The 'start_date' and 'end_date' query parameters are required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # Parse & check dates
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()

        if start_date > end_date:
            return Response(
                {"error": "'start_date' cannot be later than 'end_date'."},
                status=status.HTTP_400_BAD_REQUEST
            )

    except ValueError:
        return Response(
            {"error": "Invalid date format. Please use 'YYYY-MM-DD'."},
            status=status.HTTP_400_BAD_REQUEST
        )

    user_id = request.user.id
    if not user_id:
        return Response({'error': 'You are not authorized to access this data'}, status=status.HTTP_403_FORBIDDEN)

    # List to store all daily data
    daily_data = []

    # Loop through all dates 
    current_date = start_date
    while current_date <= end_date:
        try:
            # Fetch activity for current date
            activity = ActivityData.objects.get(
                user_id=user_id, activity_date=current_date)
            serializer = ActivityDataSerializer(activity)
            daily_data.append(serializer.data)

        except ActivityData.DoesNotExist:
            logger.warning(
                f"Data not found for user {user_id} on {current_date}, skipping.")

        # Move to next day
        current_date += timedelta(days=1)

    # Return data for the specified week
    return Response(daily_data, status=status.HTTP_200_OK)


    
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

