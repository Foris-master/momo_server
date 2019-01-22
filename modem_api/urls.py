from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from modem_api import views

urlpatterns = [
    path('modems/', views.ModemList.as_view(), name='modem-list'),
    path('modems/<int:pk>/', views.ModemDetail.as_view(), name='modem-detail'),
    path('stations/', views.StationList.as_view(), name='station-list'),
    path('stations/<int:pk>/', views.StationDetail.as_view(), name='station-detail'),
    path('service_stations/', views.ServiceStationList.as_view(), name='service-station-list'),
    path('service_stations/<int:pk>/', views.ServiceStationDetail.as_view(), name='service-station-detail'),
    path('users/', views.UserList.as_view(), name='user-list'),
    path('users/<int:pk>/', views.UserDetail.as_view(), name='user-detail'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
