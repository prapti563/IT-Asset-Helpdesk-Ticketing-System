from django.core.management.base import BaseCommand
from asset.views import check_and_escalate_tickets

class Command(BaseCommand):
    help = "Checks unresolved High/Critical tickets older than 24 hours and escalates them to the IT Manager"

    def handle(self, *args, **options):
        self.stdout.write("Checking tickets for SLA breaches...")
        check_and_escalate_tickets()
        self.stdout.write(self.style.SUCCESS("Successfully processed SLA ticket escalations."))
