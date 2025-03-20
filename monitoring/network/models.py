from django.db import models
from django.core.validators import RegexValidator
from django.conf import settings

# validator to ensure the MAC address format is correct
mac_address_validator = RegexValidator(
    regex=r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$',
    message="Enter a valid MAC address in format XX:XX:XX:XX:XX:XX."
)


class Network(models.Model):
    name = models.CharField(max_length=255, unique=True)
    admin = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="networks",
        help_text="User who administrates this network"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Host(models.Model):
    DEVICE_TYPE_CHOICES = [
        ('unknown', 'Unknown'),
        ('dns_server', 'DNS Server'),
        ('server', 'Server'),
        ('firewall', 'Firewall'),
        ('access_point', 'Access Point'),
        ('switch', 'Switch'),
    ]
    name = models.CharField(
        max_length=200,
        blank=True,
        null=True,
    )
    ip_address = models.GenericIPAddressField(
        unique=True,
    )
    mac_address = models.CharField(
        max_length=17,
        blank=True,
        null=True,
        unique=True,
        validators=[mac_address_validator],
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="hosts",
        blank=True,
        null=True
    )

    device_type = models.CharField(
        max_length=20,
        choices=DEVICE_TYPE_CHOICES,
        default='unknown',
        help_text="Select the type of device "
                  "(DNS Server, Server, Firewall, Access Point, Switch)",
    )

    network = models.ForeignKey(
        Network,
        on_delete=models.CASCADE,
        related_name="hosts",
        blank=True,
        null=True
    )

    def __str__(self):
        return self.name if self.name else self.ip_address