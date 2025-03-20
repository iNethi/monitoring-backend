import requests
from django.conf import settings

def get_cloud_token(user):
    """
    Given a user, call the cloud API login endpoint with the user's credentials
    (using their stored cloud_api_password) to get a fresh token.
    """
    login_url = settings.CLOUD_API_LOGIN_URL
    payload = {
        "username": user.username,
        "password": user.cloud_api_password,
    }
    try:
        response = requests.post(login_url, json=payload, timeout=5)
    except requests.RequestException as exc:
        return None, str(exc)
    if response.status_code == 200:
        data = response.json()
        token = data.get('token')
        return token, None
    return None, response.text
