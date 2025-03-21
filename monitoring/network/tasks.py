import subprocess
from celery import shared_task
from .models import Host, Ping
import requests
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from .models import Ping, Network
from .utils import get_cloud_token

@shared_task
def submit_ping_data():
    """
    Every 5 minutes, aggregate ping data for each network (from the last 5 minutes)
    and send it to the cloud API's ingest endpoint.

    Expected payload:
    {
      "network": <network_id>,
      "network_admin": <network_admin_identifier>,
      "data": [
         { "host": <host_id>, "is_alive": <bool>, "timestamp": <ISO8601 timestamp> },
         ...
      ]
    }
    """
    time_threshold = timezone.now() - timedelta(minutes=5)
    networks = Network.objects.all()

    for network in networks:
        # Retrieve pings for this network in the last 5 minutes.
        pings = Ping.objects.filter(network=network, timestamp__gte=time_threshold)
        if not pings.exists():
            continue  # nothing to send for this network

        # Build the data array
        data = []
        for ping in pings:
            data.append({
                "host": ping.host.id,
                "is_alive": ping.is_alive,
                "timestamp": ping.timestamp.isoformat(),
            })

        payload = {
            "network": network.id,
            "network_admin": network.admin.username,  # or another unique identifier
            "data": data,
        }

        # Obtain a fresh token using the network admin's credentials.
        token, error = get_cloud_token(network.admin)
        if not token:
            # Log the error (here we simply print; in production use proper logging)
            print(f"Failed to obtain cloud token for network {network.id}: {error}")
            continue

        headers = {"Authorization": f"Bearer {token}"}
        ingest_url = settings.CLOUD_INGEST_URL  # e.g., "https://cloud.example.com/api/ingest-uptime/"
        try:
            response = requests.post(ingest_url, json=payload, headers=headers, timeout=10)
            if response.status_code not in (200, 201):
                print(f"Cloud ingest failed for network {network.id}: {response.text}")
            else:
                print(f"Successfully ingested ping data for network {network.id}")
                # Optionally: mark these pings as sent to avoid duplicates.
                # pings.update(sent=True)
        except Exception as exc:
            print(f"Exception during cloud ingest for network {network.id}: {exc}")


def alive(ip):
    """
    Test if a host is reachable.
    Returns True if the host is reachable, False otherwise.
    """
    command = ["fping", ip]
    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    return result.returncode == 0


@shared_task
def ping_hosts():
    """
    Fetch all hosts from the DB, ping each one,
    and record the result in the PingResult model.
    """
    hosts = Host.objects.all()
    for host in hosts:
        status = alive(host.ip_address)
        # Create a new PingResult (timestamp is set automatically)
        Ping.objects.create(host=host, is_alive=status, network=host.network)

