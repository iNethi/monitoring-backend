# network/serializers.py
from rest_framework import serializers
from .models import Network, Host

class NetworkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Network
        fields = ['id', 'name', 'admin', 'created_at', 'cloud_pk']
        read_only_fields = ['id', 'created_at']


class HostSerializer(serializers.ModelSerializer):
    def validate_mac_address(self, value):
        if value == '':
            return None
        return value

    class Meta:
        model = Host
        fields = ['id', 'name', 'ip_address', 'mac_address', 'user', 'device_type', 'network', 'cloud_pk']
        read_only_fields = ['id']

