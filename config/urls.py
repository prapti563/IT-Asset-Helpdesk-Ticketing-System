from django.contrib import admin
from django.urls import path
from asset import views


urlpatterns = [

    # ==========================================
    # ADMIN
    # ==========================================

    path("admin/", admin.site.urls),

    # ==========================================
    # HOME
    # ==========================================

    path(
        "",
        views.home,
        name="home"
    ),

    # ==========================================
    # AUTHENTICATION
    # ==========================================

    path(
        "login/",
        views.login_view,
        name="login"
    ),

    path(
        "logout/",
        views.logout_view,
        name="logout"
    ),

    path(
        "register/",
        views.register_view,
        name="register"
    ),

    # ==========================================
    # DASHBOARD
    # ==========================================

    path(
        "dashboard/",
        views.dashboard,
        name="dashboard"
    ),

    # ==========================================
    # EMPLOYEES
    # ==========================================

    path(
        "employees/",
        views.employees,
        name="employees"
    ),

    path(
        "employees/<int:id>/",
        views.employee_detail,
        name="employee_detail"
    ),

    path(
        "employees/add/",
        views.employee_add,
        name="employee_add"
    ),

    # ==========================================
    # ASSETS
    # ==========================================

    path(
        "assets/",
        views.assets,
        name="assets"
    ),

    path(
        "assets/<int:id>/",
        views.asset_detail,
        name="asset_detail"
    ),

    path(
        "assets/add/",
        views.asset_add,
        name="asset_add"
    ),

    path(
        "assets/<int:id>/edit/",
        views.asset_edit,
        name="asset_edit"
    ),

    path(
        "assets/<int:id>/delete/",
        views.asset_delete,
        name="asset_delete"
    ),

    # ==========================================
    # ASSIGN / RETURN ASSET
    # ==========================================

    path(
        "assets/<int:id>/assign/",
        views.assign_asset,
        name="assign_asset"
    ),

    path(
        "assets/<int:id>/return/",
        views.return_asset,
        name="return_asset"
    ),

    # ==========================================
    # V2 — RAISE TICKET
    # ==========================================

    path(
        "assets/<int:id>/raise-ticket/",
        views.raise_ticket,
        name="raise_ticket"
    ),

    # ==========================================
    # PROFILE
    # ==========================================

   # Profile
path("profile/", views.profile, name="profile"),

# My Tickets
path(
    "my-tickets/",
    views.my_tickets,
    name="my_tickets"
),

# Activity
path("activity/", views.activity, name="activity"),
path(
    "tickets/",
    views.tickets,
    name="tickets"
),

path(
    "tickets/<int:id>/status/",
    views.update_ticket_status,
    name="update_ticket_status"
),

path(
    "tickets/<int:id>/delete/",
    views.delete_ticket,
    name="delete_ticket"
),


]