from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from asset.models import Employee, Asset, Ticket, Activity, TicketComment
import io

class AssetFlowTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        # Create standard IT Support user
        self.it_support_user = User.objects.create_user(
            username="it_admin",
            password="adminpassword",
            is_staff=True
        )
        # Create standard Employee profile and corresponding User
        self.employee = Employee.objects.create(
            employee_id="EMP001",
            name="John Doe",
            email="john@company.com",
            phone="1234567890",
            department="Engineering",
            role="Employee",
            joining_date="2026-01-01"
        )
        self.employee_user = User.objects.create_user(
            username="EMP001",
            password="employeepassword"
        )
        
        # Create an asset assigned to Employee
        self.asset = Asset.objects.create(
            asset_name="Company Laptop",
            asset_id="LAP001",
            asset_tag="TAG001",
            asset_type="Laptop",
            brand="Dell",
            model="Latitude",
            serial_number="DELL12345",
            purchase_date="2026-01-01",
            price=1200.00,
            status="Assigned",
            assigned_employee=self.employee
        )

    def test_raise_ticket_with_screenshot(self):
        # Log in as Employee
        self.client.login(username="EMP001", password="employeepassword")
        # Set session role
        session = self.client.session
        session["role"] = "employee"
        session["employee_id"] = "EMP001"
        session.save()

        # Create mock screenshot image
        image_content = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc`\x00\x00\x00\x02\x00\x01H\xaf\xa4q\x00\x00\x00\x00IEND\xaeB`\x82'
        screenshot = SimpleUploadedFile("test_error.png", image_content, content_type="image/png")

        # Post ticket raise
        response = self.client.post(
            reverse("raise_ticket", args=[self.asset.id]),
            {
                "title": "Blue screen error",
                "description": "Getting blue screen on boot",
                "category": "Hardware",
                "priority": "High",
                "screenshot": screenshot
            }
        )
        
        # Verify redirect to my_tickets
        self.assertEqual(response.status_code, 302)
        
        # Verify ticket was created in database
        ticket = Ticket.objects.get(title="Blue screen error")
        self.assertEqual(ticket.employee, self.employee)
        self.assertEqual(ticket.asset, self.asset)
        self.assertEqual(ticket.priority, "High")
        self.assertTrue(ticket.screenshot.name.endswith(".png"))

    def test_bulk_csv_import_success(self):
        # Log in as IT Support
        self.client.login(username="it_admin", password="adminpassword")
        session = self.client.session
        session["role"] = "it_support"
        session.save()

        # Create valid CSV data
        csv_data = (
            "asset_name,asset_id,asset_tag,asset_type,brand,model,serial_number,purchase_date,price,description\n"
            "Lenovo T14,LP-0010,TAG-LP10,Laptop,Lenovo,T14,S10001,2026-08-01,1100.50,Imported Laptop 1\n"
            "Lenovo T14,LP-0011,TAG-LP11,Laptop,Lenovo,T14,S10002,2026-08-01,1100.50,Imported Laptop 2\n"
        )
        csv_file = SimpleUploadedFile("assets.csv", csv_data.encode('utf-8'), content_type="text/csv")

        response = self.client.post(
            reverse("import_assets_csv"),
            {"csv_file": csv_file}
        )
        
        # Verify redirect to assets list
        self.assertEqual(response.status_code, 302)
        
        # Verify assets were created
        self.assertEqual(Asset.objects.filter(brand="Lenovo").count(), 2)
        
        # Verify activity logs were created
        activity_count = Activity.objects.filter(action="Asset Added", description__contains="CSV bulk import").count()
        self.assertEqual(activity_count, 2)

    def test_bulk_csv_import_rollback_on_error(self):
        # Log in as IT Support
        self.client.login(username="it_admin", password="adminpassword")
        session = self.client.session
        session["role"] = "it_support"
        session.save()

        # Create invalid CSV data (duplicate serial number in database, DELL12345 already exists)
        csv_data = (
            "asset_name,asset_id,asset_tag,asset_type,brand,model,serial_number,purchase_date,price,description\n"
            "HP EliteBook,LP-0020,TAG-LP20,Laptop,HP,EliteBook,S20001,2026-08-01,1300.00,HP Laptop\n"
            "HP ProBook,LP-0021,TAG-LP21,Laptop,HP,ProBook,DELL12345,2026-08-01,1000.00,Duplicate Serial Laptop\n"
        )
        csv_file = SimpleUploadedFile("assets_invalid.csv", csv_data.encode('utf-8'), content_type="text/csv")

        response = self.client.post(
            reverse("import_assets_csv"),
            {"csv_file": csv_file}
        )
        
        # Verify page re-renders (does not redirect) since there was an error
        self.assertEqual(response.status_code, 200)
        
        # Verify NO new assets were created (rollback worked)
        self.assertEqual(Asset.objects.filter(brand="HP").count(), 0)

    def test_sla_escalation_triggers(self):
        # Create a High priority ticket that is unresolved
        ticket = Ticket.objects.create(
            ticket_id="TKT9001",
            employee=self.employee,
            asset=self.asset,
            title="SLA Test Overdue",
            description="High priority issue",
            category="Hardware",
            priority="High",
            status="Open"
        )
        # Update its created_at to 25 hours ago
        Ticket.objects.filter(id=ticket.id).update(created_at=timezone.now() - timedelta(hours=25))
        
        # Log in as IT Support to trigger check on tickets view
        self.client.login(username="it_admin", password="adminpassword")
        session = self.client.session
        session["role"] = "it_support"
        session.save()
        
        response = self.client.get(reverse("tickets"))
        self.assertEqual(response.status_code, 200)
        
        # Verify ticket was escalated
        ticket.refresh_from_db()
        self.assertTrue(ticket.is_escalated)
        self.assertEqual(ticket.assigned_to.username, "it_manager")
        
        # Verify SLA Escalation activity was logged
        self.assertTrue(
            Activity.objects.filter(action="SLA Escalation", description__contains="TKT9001").exists()
        )

    def test_sla_escalation_does_not_trigger_for_recent_tickets(self):
        # Create a High priority ticket created now (0 hours ago)
        ticket = Ticket.objects.create(
            ticket_id="TKT9002",
            employee=self.employee,
            asset=self.asset,
            title="SLA Test Recent",
            description="Recent High priority issue",
            category="Hardware",
            priority="High",
            status="Open"
        )
        
        # Log in and load tickets list to trigger check
        self.client.login(username="it_admin", password="adminpassword")
        session = self.client.session
        session["role"] = "it_support"
        session.save()
        
        self.client.get(reverse("tickets"))
        
        # Verify ticket is NOT escalated
        ticket.refresh_from_db()
        self.assertFalse(ticket.is_escalated)

    def test_sla_escalation_does_not_trigger_for_low_priority(self):
        # Create a Low priority ticket that is 25 hours old
        ticket = Ticket.objects.create(
            ticket_id="TKT9003",
            employee=self.employee,
            asset=self.asset,
            title="SLA Test Low Priority",
            description="Low priority issue",
            category="Hardware",
            priority="Low",
            status="Open"
        )
        Ticket.objects.filter(id=ticket.id).update(created_at=timezone.now() - timedelta(hours=25))
        
        # Log in and load tickets list to trigger check
        self.client.login(username="it_admin", password="adminpassword")
        session = self.client.session
        session["role"] = "it_support"
        session.save()
        
        self.client.get(reverse("tickets"))
        
        # Verify ticket is NOT escalated
        ticket.refresh_from_db()
        self.assertFalse(ticket.is_escalated)
