import subprocess
from celery import shared_task
import requests
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from .models import Network, Host, Ping
from .utils import get_cloud_token
import logging

logger = logging.getLogger(__name__)

@shared_task(
    autoretry_for=(requests.RequestException, Exception),
    retry_kwargs={'max_retries': 10},
    retry_backoff=True,           # Exponential backoff (starts at 1s, doubles)
    retry_backoff_max=3600,       # Max backoff is 1 hour
    retry_jitter=True             # Add randomness to avoid thundering herd
)
def submit_ping_data():
    """
    Every 5 minutes, aggregate ping data for each network (from the last 5 minutes)
    and send it to the cloud API's ingest endpoint.

    If the cloud API is unreachable, this task will retry up to 10 times with
    exponential backoff (up to 1 hour between attempts).

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
        if not network.cloud_pk:
            continue
        # Retrieve pings for this network in the last 5 minutes.
        pings = Ping.objects.filter(network=network, timestamp__gte=time_threshold)
        if not pings.exists():
            continue  # nothing to send for this network

        # Build the data array
        data = []
        for ping in pings:
            data.append({
                "host": ping.host.cloud_pk,
                "is_alive": ping.is_alive,
                "timestamp": ping.timestamp.isoformat() if ping.timestamp else timezone.now().isoformat(),
            })

        payload = {
            "network": network.cloud_pk,
            "network_admin": network.admin.username,
            "data": data,
        }
        print(f"Payload: {payload}")
        logger.info(f"Payload: {payload}")

        # Obtain a fresh token using the network admin's credentials.
        token, error = get_cloud_token(network.admin)
        if not token:
            print(f"Token error: {error}")
            print(f"Payload: {payload}")
            raise Exception(f"Failed to obtain cloud token for network {network.id}: {error}")

        headers = {"Authorization": f"Bearer {token}"}
        ingest_url = settings.CLOUD_INGEST_URL  # e.g., "https://cloud.example.com/api/ingest-uptime/"
        try:
            response = requests.post(ingest_url, json=payload, headers=headers, timeout=10)
            if response.status_code not in (200, 201):
                print(f"API error: {response.status_code}")
                print(f"Payload: {payload}")
                raise Exception(f"Cloud ingest failed for network {network.id}")
            else:
                logger.info(f"Successfully ingested ping data for network {network.id}")
                # Optionally: mark these pings as sent to avoid duplicates.
                # pings.update(sent=True)
        except Exception as exc:
            print(f"Exception: {exc}")
            print(f"Payload: {payload}")
            raise


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
        logger.info(f"Pinged host {host.ip_address} ({host.name or ''}): {'alive' if status else 'down'}")

