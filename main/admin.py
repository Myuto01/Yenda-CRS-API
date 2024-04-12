from django.contrib import admin
from .models import User, Bus, TripSchedule

admin.site.register(User)

admin.site.register(Bus)

admin.site.register(TripSchedule)
