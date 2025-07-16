import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from .models import Network, Host
from .serializers import NetworkSerializer, HostSerializer
from .utils import get_cloud_token
import logging

logger = logging.getLogger(__name__)

# -----------------------------
# NETWORK VIEWS
# -----------------------------

class ListNetworkView(APIView):
    """
    Endpoint to list all networks for the authenticated user.
    For network admins, only networks where they are the admin are returned.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        # For simplicity, assume that only network admins create networks.
        networks = Network.objects.filter(admin=user)
        serializer = NetworkSerializer(networks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class NetworkDetailView(APIView):
    """
    Retrieve, update, or delete a network.
    Update and delete actions first call the corresponding cloud API endpoint.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        try:
            # Ensure the network belongs to the user
            return Network.objects.get(pk=pk, admin=user)
        except Network.DoesNotExist:
            return None

    def get(self, request, pk):
        network = self.get_object(pk, request.user)
        if not network:
            return Response({"error": "Network not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = NetworkSerializer(network)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        user = request.user
        network = self.get_object(pk, user)
        if not network:
            return Response({"error": "Network not found."}, status=status.HTTP_404_NOT_FOUND)

        # Obtain a fresh cloud token
        token, error = get_cloud_token(user)
        if not token:
            return Response({"error": "Failed to obtain cloud token", "details": error},
                            status=status.HTTP_400_BAD_REQUEST)

        payload = request.data.copy()

        headers = {"Authorization": f"Bearer {token}"}
        # Construct the cloud endpoint URL (assumes RESTful URL with network id)
        cloud_network_url = f"{settings.CLOUD_NETWORK_CREATE_URL}{network.cloud_pk}/"

        try:
            cloud_response = requests.put(cloud_network_url, json=payload, headers=headers, timeout=5)
        except requests.RequestException as exc:
            logger.error(f"Failed to update network on cloud: {exc}")
            return Response({"error": "Failed to update network on cloud", "details": str(exc)},
                            status=status.HTTP_502_BAD_GATEWAY)
        if cloud_response.status_code not in (200, 201):
            logger.error(f"Cloud network update failed: {cloud_response.text}")
            return Response({"error": "Cloud network update failed", "details": cloud_response.text},
                            status=cloud_response.status_code)

        serializer = NetworkSerializer(network, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        user = request.user
        network = self.get_object(pk, user)
        if not network:
            return Response({"error": "Network not found."}, status=status.HTTP_404_NOT_FOUND)
        token, error = get_cloud_token(user)
        if not token:
            return Response({"error": "Failed to obtain cloud token", "details": error},
                            status=status.HTTP_400_BAD_REQUEST)
        headers = {"Authorization": f"Bearer {token}"}
        cloud_network_url = f"{settings.CLOUD_NETWORK_CREATE_URL}{network.cloud_pk}/"
        try:
            cloud_response = requests.delete(cloud_network_url, headers=headers, timeout=5)
        except requests.RequestException as exc:
            logger.error(f"Failed to delete network on cloud: {exc}")
            return Response({"error": "Failed to delete network on cloud", "details": str(exc)},
                            status=status.HTTP_502_BAD_GATEWAY)
        if cloud_response.status_code not in (200, 204):
            logger.error(f"Cloud network deletion failed: {cloud_response.text}")
            return Response({"error": "Cloud network deletion failed", "details": cloud_response.text},
                            status=cloud_response.status_code)
        network.delete()
        return Response({"message": "Network deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


class CreateNetworkView(APIView):
    """
    Endpoint for creating a network.
    Uses token authentication locally.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        # Obtain a fresh token from the cloud API.
        token, error = get_cloud_token(user)
        if not token:
            return Response(
                {"error": "Failed to obtain cloud token", "details": error},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Prepare payload from request data.
        payload = request.data.copy()

        headers = {"Authorization": f"Bearer {token}"}
        cloud_network_url = settings.CLOUD_NETWORK_CREATE_URL
        try:
            cloud_response = requests.post(cloud_network_url, json=payload, headers=headers, timeout=5)
        except requests.RequestException as exc:
            logger.error(f"Failed to create network on cloud: {exc}")
            return Response(
                {"error": "Failed to create network on cloud", "details": str(exc)},
                status=status.HTTP_502_BAD_GATEWAY
            )
        if cloud_response.status_code not in (200, 201):
            logger.error(f"Cloud network creation failed: {cloud_response.text}")
            return Response(
                {"error": "Cloud network creation failed", "details": cloud_response.text},
                status=cloud_response.status_code
            )
        json_response = cloud_response.json()
        cloud_pk = json_response["id"]
        logger.info(f"Cloud network created: {json_response}")
        # Cloud creation succeeded; create the network locally.
        local_data = request.data.copy()
        local_data['admin'] = user.id
        local_data['cloud_pk'] = cloud_pk
        serializer = NetworkSerializer(data=local_data)
        if serializer.is_valid():
            network = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# -----------------------------
# HOST VIEWS
# -----------------------------

class ListHostView(APIView):
    """
    Endpoint to list all hosts for the authenticated user.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        # Assuming hosts are linked to the user; you could also filter by network if needed.
        hosts = Host.objects.filter(user=user)
        serializer = HostSerializer(hosts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class HostDetailView(APIView):
    """
    Retrieve, update, or delete a host.
    Update and delete actions first call the corresponding cloud API endpoint.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        try:
            # Ensure the host belongs to the user.
            return Host.objects.get(pk=pk, user=user)
        except Host.DoesNotExist:
            return None

    def get(self, request, pk):
        host = self.get_object(pk, request.user)
        if not host:
            return Response({"error": "Host not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = HostSerializer(host)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        user = request.user
        logger.info(f"Host update request: {request.data}")
        logger.info(f"user: {user}")
        host = self.get_object(pk, user)
        if not host:
            return Response({"error": "Host not found."}, status=status.HTTP_404_NOT_FOUND)
        token, error = get_cloud_token(user)
        if not token:
            return Response({"error": "Failed to obtain cloud token", "details": error},
                            status=status.HTTP_400_BAD_REQUEST)
        host_id = host.cloud_pk
        payload = request.data.copy()
        payload['network'] = host.network.cloud_pk
        logger.info(f"payloadfor cloud: {payload}")
        headers = {"Authorization": f"Bearer {token}"}
        cloud_host_url = f"{settings.CLOUD_HOST_UPDATE_URL}{host_id}/"
        
        logger.info(f"cloud_host_url: {cloud_host_url}")
        try:
            cloud_response = requests.put(cloud_host_url, json=payload, headers=headers, timeout=5)
        except requests.RequestException as exc:
            logger.error(f"Failed to update host on cloud: {exc}")
            return Response({"error": "Failed to update host on cloud", "details": str(exc)},
                            status=status.HTTP_502_BAD_GATEWAY)
        if cloud_response.status_code not in (200, 201):
            logger.error(f"Cloud host update failed: {cloud_response.text}")
            return Response({"error": "Cloud host update failed", "details": cloud_response.text},
                            status=cloud_response.status_code)
        request.data['user'] = user.id
        serializer = HostSerializer(host, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        logger.error(f"Host update failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        user = request.user
        host = self.get_object(pk, user)
        if not host:
            return Response({"error": "Host not found."}, status=status.HTTP_404_NOT_FOUND)
        token, error = get_cloud_token(user)
        if not token:
            return Response({"error": "Failed to obtain cloud token", "details": error},
                            status=status.HTTP_400_BAD_REQUEST)
        headers = {"Authorization": f"Bearer {token}"}
        cloud_host_url = f"{settings.CLOUD_HOST_DELETE_URL}"
        payload = {
            "ip_address": host.ip_address,
            "mac_address": host.mac_address,
            "network": host.network,
        }
        try:
            cloud_response = requests.delete(cloud_host_url, data=payload, headers=headers, timeout=5)
        except requests.RequestException as exc:
            logger.error(f"Failed to delete host on cloud: {exc}")
            return Response({"error": "Failed to delete host on cloud", "details": str(exc)},
                            status=status.HTTP_502_BAD_GATEWAY)
        if cloud_response.status_code not in (200, 204):
            logger.error(f"Cloud host deletion failed: {cloud_response.text}")
            return Response({"error": "Cloud host deletion failed", "details": cloud_response.text},
                            status=cloud_response.status_code)
        host.delete()
        return Response({"message": "Host deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


class CreateHostView(APIView):
    """
    Endpoint for creating a host.
    Uses token authentication locally.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        token, error = get_cloud_token(user)
        if not token:
            return Response(
                {"error": "Failed to obtain cloud token", "details": error},
                status=status.HTTP_400_BAD_REQUEST
            )
        network = Network.objects.get(pk=request.data['network'])
        payload = request.data.copy()
        payload['network'] = network.cloud_pk

        headers = {"Authorization": f"Bearer {token}"}
        cloud_host_url = settings.CLOUD_HOST_CREATE_URL
        try:
            cloud_response = requests.post(cloud_host_url, json=payload, headers=headers, timeout=5)
        except requests.RequestException as exc:
            logger.error(f"Failed to create host on cloud: {exc}")
            return Response(
                {"error": "Failed to create host on cloud", "details": str(exc)},
                status=status.HTTP_502_BAD_GATEWAY
            )
        if cloud_response.status_code not in (200, 201):
            logger.error(f"Cloud host creation failed: {cloud_response.text}")
            return Response(
                {"error": "Cloud host creation failed", "details": cloud_response.text},
                status=cloud_response.status_code
            )
        json_response = cloud_response.json()
        cloud_pk = json_response["id"]
        logger.info(f"Cloud host created: {json_response}")
        # Cloud creation succeeded; create the network locally.
        local_data = request.data.copy()
        local_data['cloud_pk'] = cloud_pk

        # Cloud call succeeded; create the host locally.
        serializer = HostSerializer(data=local_data)
        if serializer.is_valid():
            host = serializer.save(user=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
