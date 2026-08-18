from django.contrib import admin
from .models import Employee, Asset, Ticket


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):

    list_display = (
        "employee_id",
        "name",
        "email",
        "department",
        "role",
        "joining_date",
    )

    search_fields = (
        "employee_id",
        "name",
        "email",
        "department",
    )


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):

    list_display = (
        "asset_id",
        "asset_name",
        "asset_type",
        "brand",
        "status",
        "assigned_employee",
    )

    list_filter = (
        "status",
        "asset_type",
        "brand",
    )

    search_fields = (
        "asset_id",
        "asset_tag",
        "asset_name",
        "serial_number",
        "brand",
        "model",
    )


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):

    list_display = (
        "ticket_id",
        "title",
        "employee",
        "asset",
        "category",
        "priority",
        "status",
        "assigned_to",
        "created_at",
    )

    list_filter = (
        "status",
        "priority",
        "category",
    )

    search_fields = (
        "ticket_id",
        "title",
        "description",
        "employee__employee_id",
        "employee__name",
        "asset__asset_id",
        "asset__asset_name",
    )