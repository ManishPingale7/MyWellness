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
from .utils import run_flow_physical,run_flow_chat,run_flow_sleep
import requests
import os
from dotenv import load_dotenv
load_dotenv()

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
