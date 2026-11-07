from django.contrib import admin
from .models import Organization


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'email', 'phone', 'is_active')
    search_fields = ('name', 'code', 'email')