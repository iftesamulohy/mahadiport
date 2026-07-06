from django.contrib import admin

from .models import Lead


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "business", "monthly_budget", "is_read", "created_at")
    list_filter = ("is_read", "monthly_budget", "created_at")
    list_editable = ("is_read",)
    search_fields = ("name", "phone", "email", "business", "message")
    readonly_fields = ("created_at", "source_path")
    date_hierarchy = "created_at"

    @admin.action(description="Mark selected leads as read")
    def mark_read(self, request, queryset):
        queryset.update(is_read=True)

    @admin.action(description="Mark selected leads as unread")
    def mark_unread(self, request, queryset):
        queryset.update(is_read=False)

    actions = ["mark_read", "mark_unread"]
