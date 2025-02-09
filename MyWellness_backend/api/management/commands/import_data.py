import csv
from datetime import datetime
from django.core.management.base import BaseCommand
from api.models import ActivityData
from django.conf import settings
import os


class Command(BaseCommand):
    help = 'Import Fitbit data into the database from a CSV file'

    def handle(self, *args, **kwargs):
        # Define file path
        csv_file_path = os.path.join(
            settings.BASE_DIR, "ML", "fitbit_data.csv")

        # Check if file exists
        if not os.path.exists(csv_file_path):
            self.stdout.write(self.style.ERROR('CSV file not found!'))
            return

        # Open the CSV file and read data
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
                    moderately_active_distance=float(
                        row['ModeratelyActiveDistance']),
                    light_active_distance=float(row['LightActiveDistance']),
                    sedentary_active_distance=float(
                        row['SedentaryActiveDistance']),
                    very_active_minutes=int(row['VeryActiveMinutes']),
                    fairly_active_minutes=int(row['FairlyActiveMinutes']),
                    lightly_active_minutes=int(row['LightlyActiveMinutes']),
                    sedentary_minutes=int(row['SedentaryMinutes']),
                    calories=int(row['Calories']),
                ))

            # Bulk insert data into the database
            ActivityData.objects.bulk_create(activities)

        self.stdout.write(self.style.SUCCESS('Data imported successfully!'))
