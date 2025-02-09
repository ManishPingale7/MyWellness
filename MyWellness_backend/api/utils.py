def calculate_bmi(weight, height):
    """
    Calculate BMI and return category based on custom labels.

    :param weight: Weight in kilograms (kg)
    :param height: Height in centimeters (cm)
    :return: BMI value and category
    """
    height_m = height / 100  # Convert cm to meters
    bmi = weight / (height_m ** 2)  # BMI formula

    # Custom BMI categories
    if bmi < 18.5:
        category = "Normal"
    elif 18.5 <= bmi < 25:
        category = "Normal Weight"
    elif 25 <= bmi < 30:
        category = "Overweight"
    else:
        category = "Obese"

    return round(bmi, 2), category

