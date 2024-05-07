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
    path('api/v1/trip-submission/', views.TripSubmissionAPIView.as_view(), name='trip-submission'),
    path('api/v1/ticket-details/', views.TicketDetailsAPIView.as_view(), name='ticket-details'),
    path('api/v1/inactive-ticket-details/', views.InactiveTicketDetailsAPIView.as_view(), name='inactive-ticket-details'),
    path('api/v1/verify_ticket/', views.VerifyTicket.as_view(), name='verify_ticket'),
    path('api/v1/update_active_status/', views.UpdateTicketActiveStatus.as_view(), name='update-ticket-active-status'),
    path('api/v1/edit_bus/', views.EditBusView.as_view(), name='edit-bus'),
    
    #Remove
    path('login/', views    .login_view, name='login'),
    path('home/', views.home_view, name='home'),
    path('test/', views.test_view, name="test"), # CReate Bus
    path('trip-create/', views.trip_create_view, name="trip-create-view"),
    path('create-driver/', views.create_driver_details, name="create-driver"),
    path('trip-search/', views.trip_search, name="trip-search"),
    path('trip-results/', views.trip_results_view, name="trip-results"),
    path('bus-details/', views.bus_details_view, name="bus-details"),
    path('enter-passenger-details/', views.enter_passenger_details_view, name="enter-passenger-details"),
    path('confirm-details', views.confirm_passenger_details_view, name='confirm-details'),
    path('tickets.html', views.tickets_view, name='tickets'),
    path('bus_details.html', views.bus_details_view, name='bus_details'),
    path('profile/', views.profile_view, name='profile'),
    path('account-details/', views.account_details_view, name='account-details'),
    path('qr-code-scanner/', views.qr_code_scanner_view, name='qr-code-scanner'),
    path('bus-list/', views.bus_list_view, name='bus-list'),
    path('edit-bus/', views.edit_bus_view, name='edit-bus'),

]  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)