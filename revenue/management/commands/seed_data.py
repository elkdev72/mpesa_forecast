import random
from datetime import datetime, timedelta

from django.core.management.base import BaseCommand
from revenue.models import Transaction


class Command(BaseCommand):
    help = "Seed the database with sample M-PESA revenue data"

    def handle(self, *args, **kwargs):
        self.stdout.write("Deleting old data...")
        Transaction.objects.all().delete()

        today = datetime.now()
        num_days = 30

        self.stdout.write("Creating sample revenue data...")

        for i in range(num_days):
            day = today - timedelta(days=i)
            num_transactions = random.randint(5, 20)

            for _ in range(num_transactions):
                amount = random.randint(50, 1200)
                timestamp = day.replace(
                    hour=random.randint(7, 20),
                    minute=random.randint(0, 59),
                )
                Transaction.objects.create(amount=amount, timestamp=timestamp)

        self.stdout.write(self.style.SUCCESS("Database seeded successfully!"))
