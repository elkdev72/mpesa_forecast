from django.urls import path
from .views import revenue_forecast

urlpatterns = [
    path("forecast/", revenue_forecast),
]

