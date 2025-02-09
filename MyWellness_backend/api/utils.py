
import os
import requests
from dotenv import load_dotenv
load_dotenv()

#this is the langflow Physical Activity Recommendation code

def run_flow_physical(message: str) -> str:
    base_api_url = os.getenv('BASE_API_URL_PHYSICAL')
    langflow_id = os.getenv('LANGFLOW_ID_PHYSICAL')
    endpoint = os.getenv('ENDPOINT_PHYSICAL')
    physical_token = os.getenv('PHYSICAL_ACTIVITY_APPLICATION_TOKEN')

    if not all([base_api_url, langflow_id, endpoint, physical_token]):
        return "Error: Missing one or more required environment variables."

    api_url = f"{base_api_url}/lf/{langflow_id}/api/v1/run/{endpoint}"
    payload = {
        "input_value": message,
        "output_type": "text",
        "input_type": "text",
    }
    headers = {
        "Authorization": f"Bearer {physical_token}",
        "Content-Type": "application/json"
    }
    try:
        response = requests.post(api_url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return f"Error making API request: {e}"
    
    try:
        response_json = response.json()
    except ValueError as e:
        return f"Error parsing JSON response: {e}"

    try:
        outputs = response_json.get("outputs", [])
        if outputs:
            results = outputs[0].get("outputs", [])
            if results:
                text_data = results[0].get("results", {}).get("text", {}).get("text", "")
                return text_data if text_data else "No valid response received."
    except Exception as e:
        return f"Error processing response: {e}"

    return "No valid response received."




#this is the langflow Fitness Recommendation code

def run_flow_chat(message: str) -> dict:
    base_api_url = os.getenv('BASE_API_URL_CHATBOT')
    langflow_id = os.getenv('LANGFLOW_ID_CHATBOT')
    endpoint = os.getenv('ENDPOINT_CHATBOT')
    chatbot_token = os.getenv('CHATBOT_APPLICATION_TOKEN')
    
    if not all([base_api_url, langflow_id, endpoint, chatbot_token]):
        return {"error": "Missing one or more required environment variables."}
    
    api_url = f"{base_api_url}/lf/{langflow_id}/api/v1/run/{endpoint}"
    payload = {
        "input_value": message,
        "output_type": "text",
        "input_type": "text",
    }
    
    headers = {
        "Authorization": f"Bearer {chatbot_token}",
        "Content-Type": "application/json",
    }
    try:
        response = requests.post(api_url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()  
    except requests.exceptions.RequestException as e:
        return {
            "error": "Failed to get response from LangFlow API",
            "details": str(e)
        }
    
    try:
        response_json = response.json()
    except ValueError as e:
        return {"error": f"Error parsing JSON response: {e}"}
    
    try:
        outputs = response_json.get("outputs", [])
        if outputs:
            results = outputs[0].get("outputs", [])
            if results:
                text_data = results[0].get("results", {}).get("text", {}).get("text", "")
                return {"response": text_data if text_data else "No valid response received."}
        return {"error": "No valid response received."}
    except Exception as e:
        return {"error": f"Error processing response: {e}"}
    


#this is the langflow Sleep Recommendation code

def run_flow_sleep(message: str) -> str:
    base_api_url = os.getenv('BASE_API_URL_SLEEP')
    langflow_id = os.getenv('LANGFLOW_ID_SLEEP')
    endpoint_sleep = os.getenv('ENDPOINT_SLEEP')
    sleep_application_token = os.getenv('SLEEP_APPLICATION_TOKEN')
    if not all([base_api_url, langflow_id, endpoint_sleep, sleep_application_token]):
        return "Error: Missing one or more required environment variables."
    api_url = f"{base_api_url}/lf/{langflow_id}/api/v1/run/{endpoint_sleep}"
    payload = {
        "input_value": message,
        "output_type": "text",
        "input_type": "text",
    }

    headers = {
        "Authorization": f"Bearer {sleep_application_token}",
        "Content-Type": "application/json"
    }
    try:
        response = requests.post(api_url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return f"Error making API request: {e}"

    try:
        response_json = response.json()
    except ValueError as e:
        return f"Error parsing JSON response: {e}"

    try:
        outputs = response_json.get("outputs", [])
        if outputs:
            results = outputs[0].get("outputs", [])
            if results:
                text_data = results[0].get("results", {}).get("text", {}).get("text", "")
                return text_data or "No valid response received."
    except Exception as e:
        return f"Error processing response: {e}"

    return "No valid response received."

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

