from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path("api/v1/auth/bus_operator_registeration", views.RegistrationAPIView.as_view(), name="user_registeration" ),
    path("api/v1/auth/login", views.UserLoginView.as_view(), name="user_login" ),
    path('api/v1/buses/',  views.BusCreateView.as_view(), name='bus-create'),
    path('api/v1/trip-schedules/',  views.TripScheduleCreateView.as_view(), name='trip-schedule-create'),
    path('api/v1/trip-search/', views.TripSearchView.as_view(), name='trip_search'),
    path('api/v1/bus-details/<int:bus_id>/', views.BusDetailsView.as_view(), name='bus-details'),
    path('api/v1/features/', views.FeatureListView.as_view(), name='feature-list'),
    path('api/v1/create-features/', views.FeatureCreateAPIView.as_view(), name='feature-create'),
    path('api/v1/bus-list/', views.BusListView.as_view(), name='bus-list'),
    path('api/v1/create-driver-details/', views.CreateDriverDetailsAPIView.as_view(), name='create-driver-details'),
    path('bus_details.html', views.bus_details_view, name='bus_details'),

    #Remove
    
    path('test/', views.test_view, name="test"),
    path('trip-create/', views.trip_create_view, name="trip-create-view"),
    path('create-driver/', views.create_driver_details, name="create-driver"),
    path('trip-search/', views.trip_search, name="trip-search"),
    path('trip-results/', views.trip_results_view, name="trip-results"),
    path('bus-details/', views.bus_details_view, name="bus-details"),
    path('enter-passenger-details/', views.enter_passenger_details_view, name="enter-passenger-details"),
    path('confirm-details', views.confirm_passenger_details_view, name='confirm-details'),

]  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)