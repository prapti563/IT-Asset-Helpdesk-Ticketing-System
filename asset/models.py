from django.db import models
from django.contrib.auth.models import User


class Employee(models.Model):

    employee_id = models.CharField(
        max_length=20,
        unique=True
    )

    name = models.CharField(
        max_length=100
    )

    email = models.EmailField(
        unique=True
    )

    phone = models.CharField(
        max_length=15
    )

    department = models.CharField(
        max_length=100
    )

    role = models.CharField(
        max_length=100
    )

    joining_date = models.DateField()

    def __str__(self):
        return f"{self.employee_id} - {self.name}"


class Asset(models.Model):

    STATUS_CHOICES = [
        ("Available", "Available"),
        ("Assigned", "Assigned"),
        ("Repair", "Repair"),
    ]

    ASSET_TYPES = [
        ("Laptop", "Laptop"),
        ("Desktop", "Desktop"),
        ("Monitor", "Monitor"),
        ("Printer", "Printer"),
        ("Phone", "Phone"),
        ("Other", "Other"),
        ("Server", "Server"),
        ("Tablet", "Tablet"),
        ("Keyboard", "Keyboard"),
        ("Mouse", "Mouse"),
    ]

    asset_name = models.CharField(
        max_length=100
    )

    asset_id = models.CharField(
        max_length=30,
        unique=True
    )

    asset_tag = models.CharField(
        max_length=30,
        unique=True
    )

    asset_type = models.CharField(
        max_length=30,
        choices=ASSET_TYPES
    )

    brand = models.CharField(
        max_length=100
    )

    model = models.CharField(
        max_length=100
    )

    serial_number = models.CharField(
        max_length=100,
        unique=True
    )

    purchase_date = models.DateField()

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Available"
    )

    assigned_employee = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assets"
    )

    description = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.asset_id} - {self.asset_name}"


class Activity(models.Model):

    ACTION_CHOICES = [
        ("Employee Added", "Employee Added"),
        ("Employee Updated", "Employee Updated"),

        ("Asset Added", "Asset Added"),
        ("Asset Assigned", "Asset Assigned"),
        ("Asset Returned", "Asset Returned"),
        ("Sent for Repair", "Sent for Repair"),
        ("Repair Completed", "Repair Completed"),
        ("Asset Updated", "Asset Updated"),
        ("Asset Deleted", "Asset Deleted"),

        ("Login", "Login"),
        ("Logout", "Logout"),
    ]

    employee = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="activities"
    )

    asset = models.ForeignKey(
        Asset,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="activities"
    )

    action = models.CharField(
        max_length=50,
        choices=ACTION_CHOICES
    )

    description = models.TextField(
        blank=True
    )

    performed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="performed_activities"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        if self.employee:
            target = self.employee.employee_id

        elif self.asset:
            target = self.asset.asset_id

        else:
            target = "System"

        return f"{self.action} - {target}"

class Ticket(models.Model):

    PRIORITY_CHOICES = [
        ("Low", "Low"),
        ("Medium", "Medium"),
        ("High", "High"),
        ("Critical", "Critical"),
    ]

    CATEGORY_CHOICES = [
        ("Hardware", "Hardware"),
        ("Software", "Software"),
        ("Network", "Network"),
        ("Other", "Other"),
    ]

    STATUS_CHOICES = [
        ("Open", "Open"),
        ("In Progress", "In Progress"),
        ("Resolved", "Resolved"),
        ("Closed", "Closed"),
    ]

    ticket_id = models.CharField(
        max_length=20,
        unique=True
    )

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="tickets"
    )

    asset = models.ForeignKey(
        Asset,
        on_delete=models.CASCADE,
        related_name="tickets"
    )

    title = models.CharField(
        max_length=200
    )

    description = models.TextField()

    category = models.CharField(
        max_length=30,
        choices=CATEGORY_CHOICES
    )

    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default="Medium"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Open"
    )

    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tickets"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.ticket_id} - {self.title}"
class TicketComment(models.Model):
    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name="comments"
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    comment = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"Comment on {self.ticket.ticket_id}"
    
def my_tickets(request):

    # ==========================================
    # CHECK USER ROLE
    # ==========================================

    if request.session.get("role") != "employee":
        return redirect("assets")

    # ==========================================
    # GET LOGGED-IN EMPLOYEE
    # ==========================================

    employee_id = request.session.get("employee_id")

    employee = Employee.objects.filter(
        employee_id=employee_id
    ).first()

    if not employee:
        messages.error(
            request,
            "Employee profile not found."
        )
        return redirect("assets")

    # ==========================================
    # GET EMPLOYEE TICKETS
    # ==========================================

    tickets = Ticket.objects.filter(
        employee=employee
    ).select_related(
        "asset"
    ).order_by(
        "-created_at"
    )

    # ==========================================
    # SUMMARY COUNTS
    # ==========================================

    total_tickets = tickets.count()

    open_tickets = tickets.filter(
        status="Open"
    ).count()

    progress_tickets = tickets.filter(
        status="In Progress"
    ).count()

    resolved_tickets = tickets.filter(
        status="Resolved"
    ).count()

    # ==========================================
    # RENDER PAGE
    # ==========================================

    return render(
        request,
        "my_tickets.html",
        {
            "tickets": tickets,
            "total_tickets": total_tickets,
            "open_tickets": open_tickets,
            "progress_tickets": progress_tickets,
            "resolved_tickets": resolved_tickets,
        }
    )
# =========================
# IT SUPPORT — ALL TICKETS
# =========================

def tickets(request):

    if not request.user.is_authenticated:
        return redirect("login")

    if request.session.get("role") != "it_support":
        return redirect("dashboard")

    tickets = Ticket.objects.select_related(
        "employee",
        "asset",
        "assigned_to"
    ).order_by(
        "-created_at"
    )

    total_tickets = tickets.count()

    open_tickets = tickets.filter(
        status="Open"
    ).count()

    progress_tickets = tickets.filter(
        status="In Progress"
    ).count()

    resolved_tickets = tickets.filter(
        status="Resolved"
    ).count()

    closed_tickets = tickets.filter(
        status="Closed"
    ).count()

    return render(
        request,
        "tickets.html",
        {
            "tickets": tickets,
            "total_tickets": total_tickets,
            "open_tickets": open_tickets,
            "progress_tickets": progress_tickets,
            "resolved_tickets": resolved_tickets,
            "closed_tickets": closed_tickets,
        }
    )


# =========================
# IT SUPPORT — UPDATE STATUS
# =========================

def update_ticket_status(request, id):

    if not request.user.is_authenticated:
        return redirect("login")

    if request.session.get("role") != "it_support":
        return redirect("dashboard")

    ticket = get_object_or_404(
        Ticket,
        id=id
    )

    if request.method == "POST":

        new_status = request.POST.get(
            "status"
        )

        valid_statuses = [
            choice[0]
            for choice in Ticket.STATUS_CHOICES
        ]

        if new_status not in valid_statuses:

            messages.error(
                request,
                "Invalid ticket status."
            )

            return redirect("tickets")

        ticket.status = new_status

        # Assign ticket to current IT Support
        ticket.assigned_to = request.user

        ticket.save()

        messages.success(
            request,
            f"{ticket.ticket_id} status updated to {new_status}."
        )

        return redirect("tickets")

    return redirect("tickets")
# =========================
# IT SUPPORT — DELETE TICKET
# =========================

def delete_ticket(request, id):

    if not request.user.is_authenticated:
        return redirect("login")

    if request.session.get("role") != "it_support":
        return redirect("dashboard")

    ticket = get_object_or_404(
        Ticket,
        id=id
    )

    if request.method == "POST":

        ticket_id = ticket.ticket_id

        ticket.delete()

        messages.success(
            request,
            f"Ticket {ticket_id} deleted successfully."
        )

        return redirect("tickets")

    return render(
        request,
        "ticket_confirm_delete.html",
        {
            "ticket": ticket
        }
    )