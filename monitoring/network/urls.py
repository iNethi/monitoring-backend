from django.urls import path
from .views import (
    CreateNetworkView, ListNetworkView, NetworkDetailView,
    CreateHostView, ListHostView, HostDetailView
)

urlpatterns = [
    # Network endpoints
    path('networks/', ListNetworkView.as_view(), name='list-networks'),
    path('networks/create/', CreateNetworkView.as_view(), name='create-network'),
    path('networks/<int:pk>/', NetworkDetailView.as_view(), name='network-detail'),

    # Host endpoints
    path('hosts/', ListHostView.as_view(), name='list-hosts'),
    path('hosts/create/', CreateHostView.as_view(), name='create-host'),
    path('hosts/<int:pk>/', HostDetailView.as_view(), name='host-detail'),
]
