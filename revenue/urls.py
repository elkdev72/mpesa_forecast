from django.urls import path
from .views import revenue_forecast
from .views import UploadCSVView, TransactionListView       
from .views import upload_csv_template


urlpatterns = [
    path("forecast/", revenue_forecast),
    path('upload/', UploadCSVView.as_view(), name='upload-csv'),
    path('transactions/', TransactionListView.as_view(), name='transactions'),
    path('upload-form/', upload_csv_template, name='upload-form'),
    
]

