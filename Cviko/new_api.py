import requests # install requests package
import json

url = "http://127.0.0.1:8000"

def get_token(username: str = "student", password: str = "student"):
    token = json.loads(requests.post(url + "/token", data={"username": username, "password": password}).text)
    return token["access_token"]

def get_weather(token: str):
    response = requests.get(url + "/weather", headers={"Authorization": "Bearer " + token})
    return response.text

token = get_token()
print(get_weather(token))

# Get currency exchange rates

# Get VAT rates

# Get VAT rate for specific country

# Read up on HTTP methods and response codes

# Check out the link
