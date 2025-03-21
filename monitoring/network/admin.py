from django.contrib import admin
from .models import Network, Host, Ping

@admin.register(Network)
class NetworkAdmin(admin.ModelAdmin):
    list_display = ('name', 'admin', 'created_at')
    search_fields = ('name', 'admin__username')
    ordering = ('-created_at',)


@admin.register(Host)
class HostAdmin(admin.ModelAdmin):
    list_display = ('name', 'ip_address', 'mac_address', 'user', 'network', 'device_type')
    search_fields = ('name', 'ip_address', 'mac_address', 'user__username', 'network__name')
    ordering = ('name',)


@admin.register(Ping)
class PingAdmin(admin.ModelAdmin):
    list_display = ('host', 'is_alive', 'timestamp', 'network')
    list_filter = ('is_alive', 'network')
    ordering = ('-timestamp',)
