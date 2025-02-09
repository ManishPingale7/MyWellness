from api.models import ActivityData
import csv
import os
from datetime import datetime
from django.conf import settings
import django

# Django setup
# Replace with your actual settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MyWellness_backend.settings')
django.setup()

# Absolute import for the model

# File path
csv_file_path = os.path.join(settings.BASE_DIR, "ML", "fitbit_data.csv")

# Read and process CSV
with open(csv_file_path, newline="", encoding="utf-8") as csvfile:
    reader = csv.DictReader(csvfile)

    activities = []
    for row in reader:
        activities.append(ActivityData(
            user_id=int(row['User_ID']),
            activity_date=datetime.strptime(
                row['ActivityDate'], "%Y-%m-%d").date(),
            total_steps=int(row['TotalSteps']),
            total_distance=float(row['TotalDistance']),
            very_active_distance=float(row['VeryActiveDistance']),
            moderately_active_distance=float(row['ModeratelyActiveDistance']),
            light_active_distance=float(row['LightActiveDistance']),
            sedentary_active_distance=float(row['SedentaryActiveDistance']),
            very_active_minutes=int(row['VeryActiveMinutes']),
            fairly_active_minutes=int(row['FairlyActiveMinutes']),
            lightly_active_minutes=int(row['LightlyActiveMinutes']),
            sedentary_minutes=int(row['SedentaryMinutes']),
            calories=int(row['Calories']),
        ))

    # Bulk insert to the database
    ActivityData.objects.bulk_create(activities)

print("Data imported successfully!")
