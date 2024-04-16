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


    #Remove
    path('test/', views.test_view, name="test")
]  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)