import pandas as pd
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Transaction

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

