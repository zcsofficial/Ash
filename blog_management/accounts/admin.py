from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    # Define fields to display in the admin panel for CustomUser
    model = CustomUser
    fieldsets = UserAdmin.fieldsets + (  # Extend default UserAdmin fields
        ('Additional Info', {'fields': ('profile_picture', 'contact_number')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('profile_picture', 'contact_number')}),
    )
