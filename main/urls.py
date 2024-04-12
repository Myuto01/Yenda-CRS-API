from django.urls import path
from . import views


urlpatterns = [
    path("api/v1/auth/bus_operator_registeration", views.RegistrationAPIView.as_view(), name="user_registeration" ),
    path("api/v1/auth/login", views.UserLoginView.as_view(), name="user_login" ),
    path('api/v1/buses/',  views.BusCreateView.as_view(), name='bus-create'),
    path('api/v1/trip-schedules/',  views.TripScheduleCreateView.as_view(), name='trip-schedule-create'),
    path('api/v1/trip-search/', views.TripSearchView.as_view(), name='trip_search'),

]