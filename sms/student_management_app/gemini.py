import requests

GEMINI_API_KEY = 'AIzaSyAOAHfibh07ddBHQ2c8oPKt5-tiN2i3RSQ'

def ask_gemini(question):
    headers = {
        'Authorization': f'Bearer {GEMINI_API_KEY}',
        'Content-Type': 'application/json',
    }
    data = {
        'question': question
    }
    try:
        response = requests.post('https://api.gemini.com/v1/ask', headers=headers, json=data)
        response.raise_for_status()  # This will raise an HTTPError if the response was unsuccessful
        return response.json()
    except requests.exceptions.RequestException as e:
        return {'error': str(e)}
