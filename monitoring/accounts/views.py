# accounts/views.py
import requests
from django.conf import settings
from rest_framework.views import APIView
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny
from .serializers import CustomUserRegistrationSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
import logging

User = get_user_model()

logger = logging.getLogger(__name__)


class LocalLoginView(ObtainAuthToken):
    """
    Login endpoint for local API.
    Accepts username and password, and returns an authentication token.
    """
    def post(self, request, *args, **kwargs):
        # Validate the credentials using DRF's built-in serializer
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        # Create or get an authentication token for the user
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'username': user.username,
        })


class RegisterView(APIView):
    """
    Registration endpoint.
    It sends the provided credentials to the cloud API for verification.
    If successful, it creates a local user (storing the cloud API password)
    and returns a local token.
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = CustomUserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']

            # Prepare payload for cloud API login endpoint.
            cloud_payload = {
                "username": username,
                "password": password,
            }

            # URL of your cloud API login endpoint
            cloud_api_url = settings.CLOUD_API_LOGIN_URL  # e.g. "https://cloud.example.com/api/network-admin/login/"

            try:
                cloud_response = requests.post(cloud_api_url, json=cloud_payload, timeout=5)

            except requests.RequestException as exc:
                return Response(
                    {"error": "Failed to connect to cloud API", "details": str(exc)},
                    status=status.HTTP_502_BAD_GATEWAY
                )

            if cloud_response.status_code != 200:
                try:
                    error_details = cloud_response.json()
                except ValueError:
                    error_details = cloud_response.text
                return Response(
                    {"error": "Cloud API authentication failed", "details": error_details},
                    status=cloud_response.status_code
                )

            try:
                cloud_data = cloud_response.json()
            except ValueError as e:
                return Response(
                    {"error": "Cloud API returned invalid JSON", "details": str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
            cloud_token = cloud_data.get('token')
            if not cloud_token:
                return Response(
                    {"error": "Cloud API did not return a token."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Create local user and store the cloud API password for later use.
            try:
                user = serializer.save()
                user.cloud_api_password = password
                user.save()
            except Exception as e:
                return Response(
                    {"error": "Failed to create local user", "details": str(e)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            # Generate a local authentication token (if you're using DRF token authentication)
            token_obj, _ = Token.objects.get_or_create(user=user)

            return Response({
                "message": "Registration successful.",
                "cloud_token": cloud_token,
                "local_token": token_obj.key,
                "user": serializer.data,
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
