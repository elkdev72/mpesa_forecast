import pandas as pd
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Transaction
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from rest_framework import status
from rest_framework import generics
from .serializers import TransactionSerializer

@api_view(['GET'])
def revenue_forecast(request):
    # Get all transactions
    qs = Transaction.objects.all().order_by('timestamp')

    if qs.count() < 3:
        return Response({"error": "Not enough data to forecast"}, status=400)

    # Convert to DataFrame
    df = pd.DataFrame(list(qs.values('timestamp', 'amount')))
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df.set_index('timestamp', inplace=True)

    # Resample daily and sum sales
    daily = df['amount'].resample('D').sum()

    # Simple moving average (7-day)
    forecast_value = daily.tail(7).mean()

    # Forecast next 7 days
    future_dates = pd.date_range(start=daily.index[-1] + pd.Timedelta(days=1), periods=7)

    forecast = {str(date.date()): float(forecast_value) for date in future_dates}

    return Response({
        "last_7_days_avg": float(forecast_value),
        "forecast_next_7_days": forecast
    })




class UploadCSVView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        file = request.FILES.get('file')

        if not file:
            return Response({"error": "No file uploaded."}, status=400)

        try:
            df = pd.read_csv(file)

            # require columns
            if 'amount' not in df.columns or 'timestamp' not in df.columns:
                return Response({
                    "error": "CSV must contain 'amount' and 'timestamp' columns."
                }, status=400)

            # save each row
            for _, row in df.iterrows():
                Transaction.objects.create(
                    amount=row['amount'],
                    timestamp=row['timestamp']
                )

            return Response({"message": "CSV uploaded and data saved."})
        except Exception as e:
            return Response({"error": str(e)}, status=500)
        

class TransactionListView(generics.ListAPIView):
    queryset = Transaction.objects.all().order_by('-timestamp')
    serializer_class = TransactionSerializer




from django.shortcuts import render
from .models import Transaction
import pandas as pd

def upload_csv_template(request):
    message = error = None

    if request.method == 'POST':
        file = request.FILES.get('file')
        if not file:
            error = "No file selected."
        else:
            try:
                df = pd.read_csv(file)
                if 'amount' not in df.columns or 'timestamp' not in df.columns:
                    error = "CSV must contain 'amount' and 'timestamp' columns."
                else:
                    for _, row in df.iterrows():
                        Transaction.objects.create(
                            amount=row['amount'],
                            timestamp=row['timestamp']
                        )
                    message = "CSV uploaded and saved successfully!"
            except Exception as e:
                error = str(e)

    return render(request, 'revenue/upload.html', {"message": message, "error": error})
