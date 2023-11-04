import requests  # install requests package
import json

port = 9000
url = f"http://127.0.0.1:{port}"


def get_token(username: str = "student", password: str = "student") -> str:
    token = json.loads(requests.post(url + "/token", data={"username": username, "password": password}).text)
    return token["access_token"]


def get_weather(token: str) -> str:
    response = requests.get(url + "/weather", headers={"Authorization": "Bearer " + token})
    return response.text


token = get_token()
print(get_weather(token))

# Get currency exchange rates

# Get VAT rates

# Get VAT rate for specific country

# Read up on HTTP methods and response codes

# Check out the link
