from .models import ActivityData
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser
from .utils import calculate_bmi

"""
Required values:
[ STATIC - AGE,BMI_CODE,GENDER_CODE,OCCUPATION_CODE,
Sleep Duration,Quality of Sleep,Physical Activity Level,Heart Rate,Daily Steps,
systolic,diastolic]

OUTPUT values:
    {'None': 0, 'Insomnia': 1, 'Sleep Apnea': 1}

INPUT values:

Ordinal Encoder:
    1)BMI Category
    Normal Weight  0                    
    Normal         1                   
    Overweight     2                   
    Obese          3                    

Label Encoder:
    1)Gender
    Male           1             
    Female         0    

    2)Occupation             
    Accountant            0                 
    Doctor                1                 
    Engineer              2                 
    Lawyer                3                 
    Manager               4        
    Nurse                 5                 
    Sales Representative  6                  
    Salesperson           7                 
    Scientist             8                  
    Software Engineer     9                  
    Teacher               10      

Standard Scaler -> all          
"""


class SleepDisorderSerializer(serializers.Serializer):
    sleep_duration = serializers.FloatField()
    quality_of_sleep = serializers.FloatField()
    physical_activity_level = serializers.FloatField()
    stress_level = serializers.FloatField()
    heart_rate = serializers.FloatField()
    daily_steps = serializers.IntegerField()
    bmi_category_cod = serializers.IntegerField()
    systolic = serializers.IntegerField()
    diastolic = serializers.IntegerField()


class ActivityDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityData
        fields = [
            'user_id',
            'activity_date',
            'total_steps',
            'total_distance',
            'very_active_distance',
            'moderately_active_distance',
            'light_active_distance',
            'sedentary_active_distance',
            'very_active_minutes',
            'fairly_active_minutes',
            'lightly_active_minutes',
            'sedentary_minutes',
            'calories'
        ]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'password', 'name',
                  'age', 'gender', 'height', 'weight', 'occupation']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            **validated_data)  # Ensures password is hashed
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user_id': user.id
        }
